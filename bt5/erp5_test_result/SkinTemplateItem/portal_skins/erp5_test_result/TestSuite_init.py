# Required to avoid useless writes on disk
# and to have some database for tests
context.setClusterConfiguration("""{"mariadb": {
  "relaxed-writes": true,
  "mariadb-relaxed-writes": true,
  "test-database-amount": 30}
}""")
