package db

import (
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

type Person struct {
	gorm.Model
	FirstName string
	LastName  string
}

func initialize() *gorm.DB {
	db, err := gorm.Open(sqlite.Open("test.db"), &gorm.Config{})
	if err != nil {
		panic("failed to connect database")
	}

	// Migrate the schema
	err = db.AutoMigrate(&Person{})
	if err != nil {
		return nil
	}

	return db
}

func CreateUser(firstName string, lastName string) {
	db := initialize()
	db.Create(&Person{FirstName: firstName, LastName: lastName})
}

func GetUser() Person {
	db := initialize()
	var person Person
	db.First(&person, 1)

	return person
}
