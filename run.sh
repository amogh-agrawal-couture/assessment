set -e
docker-compose up -d
python data_generator.py --customers 1000 --products 300 --orders 8000