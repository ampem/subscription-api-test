alembic revision --autogenerate -m "add simulation column to plans"
alembic upgrade head
# Inside the container
docker compose exec api python scripts/generate_seed_data.py --users 100 --output seed_data.sql
# Then apply to database
docker compose exec api sh -c "mysql -h db -u shade -pshade shade < seed_data.sql"
