

Open terminal in the folder containing this repository and run:


1. caffeinate python3 src/get_product_data.py   to get product's information  

2. for file in data/raw/*.csv; do
	caffeinate python3 src/get_bought_number.py "$file"
	done

To get bought number for each product.






