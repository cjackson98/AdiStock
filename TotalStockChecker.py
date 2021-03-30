import json
import requests
import datetime

class adidasInfo:
    
    def __init__(self, pid, debug=False):

        self.pid = pid.upper()
        self.headers = {'User-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}

        self.stock_url = "https://www.adidas.com/on/demandware.store/Sites-adidas-US-Site/en_US/Product-GetAvailability?pid={}&Quantity=1000000".format(self.pid)
        self.au_stock  = "https://www.adidas.com.au/on/demandware.store/Sites-adidas-AU-Site/en_AU/Product-GetAvailability?pid={}&Quantity=1000000".format(self.pid)
        self.gb_stock  = "https://www.adidas.co.uk/on/demandware.store/Sites-adidas-GB-Site/en_GB/Product-GetAvailability?pid={}&Quantity=1000000".format(self.pid)
        self.ca_stock  = "https://www.adidas.ca/on/demandware.store/Sites-adidas-CA-Site/en_CA/Product-GetAvailability?pid={}&Quantity=1000000".format(self.pid)

        self.info_url = "https://www.adidas.com/api/products/{}".format(self.pid)
        self.avail_url = "https://www.adidas.com/api/products/{}/availability".format(self.pid)

        print("Getting data for {}. . .".format(self.pid))

        #########################################################################################################
        # Use requests to get data for the URLs. Set appropriate variables to indicate success/validity
        #########################################################################################################
        # Stock Data
        try:
            self.r_stock = requests.get(url=self.stock_url, headers=self.headers, timeout=5)
            self.stock_data = json.loads(self.r_stock.text)
            self.stock_success = True
        except:
            self.stock_success = False
            self.stock_data = None
            self.r_stock = None


        # Info Data
        try:
            self.r_info = requests.get(url=self.info_url, headers=self.headers, timeout=5)
            self.info_data = json.loads(self.r_info.text)
            self.info_success = True
        except:
            self.info_success = False
            self.info_data = None
            self.r_info = None


        # Availability Data
        try:
            self.r_avail = requests.get(url=self.avail_url, headers=self.headers, timeout=5)
            self.avail_data = json.loads(self.r_avail.text)
            self.avail_success = True
        except:
            self.avail_success = False
            self.avail_data = None
            self.r_avail = None


        try:
            self.au = requests.get(url=self.au_stock, headers=self.headers, timeout=5)
            self.au_data = json.loads(self.au.text)
        except:
            self.au = None

        try:
            self.gb = requests.get(url=self.gb_stock, headers=self.headers, timeout=5)
            self.gb_data = json.loads(self.gb.text)
        except:
            self.gb = None

        try:
            self.ca = requests.get(url=self.ca_stock, headers=self.headers, timeout=5)
            self.ca_data = json.loads(self.ca.text)
        except:
            self.ca = None



        #########################################################
        # Check for validity of data
        #########################################################
        # Check Info Validity
        self.info_valid = True
        try:
            if "message" in self.info_data:
                if self.info_data["message"] == "Product not found" or self.info_data["message"] == "Product redirect":
                    self.info_valid = False
        except:
            self.avail_valid = True


        # Check Availability Validity
        self.avail_valid = True
        try:
            if "availability_status" in self.avail_data:
                if self.avail_data["availability_status"] == "PREVIEW":
                    self.avail_valid = False
            elif "message" in self.avail_data:
                if self.avail_data["message"] == "not found":
                    self.avail_valid = False
            else:
                self.avail_valid = True
        except:
            self.avail_valid = True


        # Check Stock Validity
        self.stock_valid = True
        try:
            self.stock_data["avLevels"]["IN_STOCK"]
            self.stock_data["avLevels"]["PREORDER"]
            self.stock_data["avLevels"]["BACKORDER"]
        except:
            self.stock_valid = False
        


        ###############################################
        # Used for debugging
        ###############################################
        if debug:
            print( "Info - Success: {} - Valid: {}".format(self.info_success, self.info_valid) )
            print( "Avail - Success: {} - Valid: {}".format(self.avail_success, self.avail_valid) )
            print( "Stock - Success: {} - Valid: {}".format(self.stock_success, self.stock_valid) )
            print()
            print("Stock data: {}".format(self.stock_url))
            print("Product information: {}".format(self.info_url))
            print("Availability data: {}".format(self.avail_url))

    def get_product_url(self):
        if self.info_success and self.info_valid:
            return "https://" + self.info_data["meta_data"]["canonical"][2:]
        else:
            return None

    def get_price(self):
        if self.info_success and self.info_valid:
            return "${}".format(self.info_data["pricing_information"]["currentPrice"])
        else:
            return None

    def get_splash_page(self):
        if self.info_success and self.info_valid:
            return self.info_data["attribute_list"]["isWaitingRoomProduct"]
        else:
            return None

    def get_total_stock(self):
        stock = ""
        us_total_stock = 0
        gb_total_stock = 0
        ca_total_stock = 0
        au_total_stock = 0

        if self.stock_success:
            us_total_stock = int(self.stock_data["avLevels"]["IN_STOCK"])
            stock = stock + "US In Stock: {}\n".format( us_total_stock )
        if self.gb:
            gb_total_stock = int(self.gb_data["avLevels"]["IN_STOCK"])
            stock = stock + "UK In Stock: {}\n".format( gb_total_stock )
        if self.ca:
            ca_total_stock = int(self.ca_data["avLevels"]["IN_STOCK"])
            stock = stock + "CA In Stock: {}\n".format( ca_total_stock )
        if self.au:
            au_total_stock = int(self.au_data["avLevels"]["IN_STOCK"])
            stock = stock + "AU In Stock: {}\n".format( au_total_stock )

        if len(stock) == 0:
            return None
        else:
            total = us_total_stock + gb_total_stock + ca_total_stock + au_total_stock
            stock = stock + "Total In Stock: {}".format( total )
            return stock

    def get_availability(self):
        availability = ""
        if self.avail_success and self.avail_valid:
            sizes, size_codes = self.get_sizes()
            ctr = 0
            for size in size_codes:
                try:
                    url = "https://www.adidas.com/on/demandware.store/Sites-adidas-US-Site/en_US/Product-GetAvailability?pid={}&Quantity=1000000".format(size)
                    req = requests.get(url=url, headers=self.headers, timeout=5)
                    data = json.loads(req.text)
                    availability = availability + "Size {} has {} pairs in stock.\n".format( sizes[ctr], int( data["avLevels"]["IN_STOCK"] ) )
                    ctr += 1
                except:
                    availability = availability + "Error getting info."
                    continue
            return availability
        else:
            return None

    def get_images(self):
        if self.info_success and self.info_valid:
            for x in self.info_data["view_list"]:
                yield x["image_url"]
        else:
            return None

    def get_urls(self):
        return "Stock Data: {}\nProduct Information: {}\nAvailability Data: {}".format(self.stock_url, self.info_url, self.avail_url)

    def get_release_date(self):
        if self.info_success and self.info_valid:
            release_date = datetime.datetime.strptime(self.info_data["attribute_list"]["preview_to"],"%Y-%m-%dT%H:%M:%S.%fZ")
            formatted_relase_date = release_date.strftime("%m/%d/%Y at %I:%M:%S %p")
            return formatted_relase_date + " PST"
        elif self.stock_success and len(self.stock_data["inStockDate"]) > 1:
            release_date = datetime.datetime.strptime(self.stock_data["inStockDate"],"%Y-%m-%dT%H:%M:%S.%fZ")
            formatted_relase_date = release_date.strftime("%m/%d/%Y at %I:%M:%S %p")
            return formatted_relase_date + " PST"
        else:
            return None

    def get_keywords(self):
        if self.info_success and self.info_valid:
            return self.info_data["meta_data"]["keywords"]
        else:
            return None

    def get_color(self):
        if self.info_success and self.info_valid:
            return self.info_data["attribute_list"]["color"]
        else:
            return None
    
    def get_availability_status(self):
        if self.avail_success and self.avail_valid:
            return self.avail_data["availability_status"]
        elif self.stock_success:
            return self.stock_data["avStatus"]
        else:
            return None

    def get_in_stock(self):
        if self.stock_success:
            return self.stock_data["inStock"]
        else:
            return None

    def get_type(self):
        if self.info_success and self.info_valid:
            return '"' + self.info_data["product_type"] + '"'
        else:
            return None

    def get_name(self):
        if self.info_success and self.info_valid:
            return self.info_data["name"]
        else:
            return None

    def get_description(self):
        if self.info_success and self.info_valid:
            return self.info_data["meta_data"]["description"]
        else:
            return None

    def get_sizes(self):
        sizes = []
        size_codes = []
        if self.avail_success and self.avail_valid:
            for x in self.avail_data["variation_list"]:
                 size_codes.append( x["sku"] )
                 sizes.append( x["size"] )
            return sizes, size_codes
        else:
            return None
