package deskconn

import (
	"encoding/json"
	"fmt"
	"io"

	"github.com/pion/webrtc/v4"
)

const (
	p2pMsgControl byte = iota // encrypted JSON control message (fsRequest/fsResponse)
	p2pMsgData                // encrypted raw chunk bytes
)

// sendEncryptedJSON JSON-marshals v, encrypts it with key, and sends it on
// channel as a p2pMsgControl envelope.
func sendEncryptedJSON(channel *webrtc.DataChannel, v any, key []byte) error {
	plaintext, err := json.Marshal(v)
	if err != nil {
		return err
	}
	return sendEncryptedEnvelope(channel, p2pMsgControl, plaintext, key)
}

func sendEncryptedEnvelope(channel *webrtc.DataChannel, kind byte, plaintext, key []byte) error {
	ciphertext, err := EncryptPayload(plaintext, key)
	if err != nil {
		return err
	}
	envelope := make([]byte, 1+len(ciphertext))
	envelope[0] = kind
	copy(envelope[1:], ciphertext)
	return channel.Send(envelope)
}

// decryptEnvelope splits a received binary message into its kind byte and
// decrypted plaintext.
func decryptEnvelope(data []byte, key []byte) (kind byte, plaintext []byte, err error) {
	if len(data) < 1 {
		return 0, nil, fmt.Errorf("empty message")
	}
	plaintext, err = DecryptPayload(data[1:], key)
	if err != nil {
		return 0, nil, err
	}
	return data[0], plaintext, nil
}

// sendEncryptedBytes writes data to channel as fileStreamChunkSize
// plaintext chunks, each individually encrypted and sent as its own
// p2pMsgData envelope, blocking on sendReady/closed whenever the channel's
// send buffer is over fileStreamMaxBuffered.
func sendEncryptedBytes(channel *webrtc.DataChannel, closed, sendReady <-chan struct{}, data, key []byte) error {
	for len(data) > 0 {
		select {
		case <-closed:
			return io.ErrClosedPipe
		default:
		}

		n := fileStreamChunkSize
		if n > len(data) {
			n = len(data)
		}

		ciphertext, err := EncryptPayload(data[:n], key)
		if err != nil {
			return err
		}
		envelope := make([]byte, 1+len(ciphertext))
		envelope[0] = p2pMsgData
		copy(envelope[1:], ciphertext)

		for channel.BufferedAmount()+uint64(len(envelope)) > fileStreamMaxBuffered {
			select {
			case <-sendReady:
			case <-closed:
				return io.ErrClosedPipe
			}
		}

		if err := channel.Send(envelope); err != nil {
			return err
		}
		data = data[n:]
	}
	return nil
}

// p2pServerKeyExchange performs the server side of the per-channel key
// exchange. firstMessage is the client's plaintext public key, already
// consumed by xconn-webrtc-go to classify the channel, so it's parsed
// directly rather than read again off the channel. Sends back our
// own plaintext public key and returns the derived session keys; every
// message from here on is encrypted.
func p2pServerKeyExchange(channel *webrtc.DataChannel, firstMessage []byte) (sendKey, receiveKey []byte, err error) {
	var clientKey keyExchangeMsg
	if err := json.Unmarshal(firstMessage, &clientKey); err != nil {
		return nil, nil, err
	}
	if len(clientKey.PublicKey) != 32 {
		return nil, nil, fmt.Errorf("invalid client public key length: %d", len(clientKey.PublicKey))
	}

	publicKey, sendKey, receiveKey, err := ServerKeyExchange(clientKey.PublicKey)
	if err != nil {
		return nil, nil, err
	}
	if err := sendWebRTCJSON(channel, keyExchangeMsg{PublicKey: publicKey}); err != nil {
		return nil, nil, err
	}
	return sendKey, receiveKey, nil
}

// p2pClientKeyExchange performs the client side of the per-channel key
// exchange on a freshly opened channel: send our plaintext public key as
// the channel's first message, wait for the peer's, derive session keys.
func p2pClientKeyExchange(channel *webrtc.DataChannel, closed <-chan struct{}) (sendKey, receiveKey []byte, err error) {
	publicKey, privateKey, err := CreateX25519KeyPair()
	if err != nil {
		return nil, nil, err
	}

	peerKeyCh := make(chan keyExchangeMsg, 1)
	channel.OnMessage(func(msg webrtc.DataChannelMessage) {
		if !msg.IsString {
			return
		}
		var peerKey keyExchangeMsg
		if json.Unmarshal(msg.Data, &peerKey) == nil {
			select {
			case peerKeyCh <- peerKey:
			default:
			}
		}
	})

	if err := sendWebRTCJSON(channel, keyExchangeMsg{PublicKey: publicKey}); err != nil {
		return nil, nil, err
	}

	peerKey, err := recvPriority(peerKeyCh, closed, p2pRequestTimeout)
	if err != nil {
		return nil, nil, err
	}
	if len(peerKey.PublicKey) != 32 {
		return nil, nil, fmt.Errorf("invalid peer public key length: %d", len(peerKey.PublicKey))
	}

	return ClientKeyExchangeKeys(privateKey, peerKey.PublicKey)
}
