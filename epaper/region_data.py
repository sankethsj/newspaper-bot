import datetime as dt
import json
import os


PATH_TO_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json')


class Region(object):

    def __init__(self) -> None:

        with open(PATH_TO_DATA) as fo:
            data = json.loads(fo.read())

        self.data = data

    def get_availabe_regions(self):

        data = [region for region in self.data]

        return data

    def get_region_info(self, region):

        return self.data.get(region)
        

    def set_region_info(self, region, paper_code, date=None):

        if self.data.get(region) is None:
            return False

        if date is None:
            date = dt.datetime.now().strftime("%d-%m-%Y")
            
        self.data[region]["paper_code"][date] = paper_code

        with open(PATH_TO_DATA, "w") as fo:
            json.dump(self.data, fo, indent=4, sort_keys=True)

        return True

    def get_region_code(self, region):

        data = self.data.get(region)

        if data is None:
            return None
        
        return data.get('region_code')

    def get_paper_code(self, region, date):

        data = self.data.get(region)

        if data is None:
            return None
        
        return data['paper_code'].get(date)


# region_data = Region()

# print(region_data.get_region_info("Bengaluru"))

# print(region_data.get_paper_code("Bengaluru", "14-08-2021"))
