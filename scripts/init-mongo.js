db.createUser(
  {
    user: "disguisedcat",
    pwd: "123456",
    roles: [{role: "readWrite", db: "disguisedcats"}]
  }
)
