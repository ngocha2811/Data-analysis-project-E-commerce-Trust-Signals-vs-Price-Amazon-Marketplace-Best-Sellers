

Open terminal in the folder containing this repository and run:

1. python3 src/get_category_path.py   to get category paths.

2. caffeinate python3 src/get_product_data.py   to get product's information  

3. for file in data/raw/*.csv; do
	caffeinate python3 src/get_bought_number.py "$file"
	done







