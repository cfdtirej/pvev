import math


class PoinToMesh:

    def __init__(self, lon, lat):
        self.lon = lon
        self.lat = lat

    # 1次メッシュ
    def mesh_1st(self):
        return int(math.floor(self.lat*1.5)) * 100 + int(math.floor(self.lon-100))

    # 2次メッシュ
    def mesh_2nd(self):
        return (
           int(math.floor(self.lat*12 / 8)) * 10000 + int(math.floor((self.lon-100)*8 / 8)) * 100 +
           int(math.floor(self.lat*12 % 8)) * 10 + int(math.floor((self.lon-100)*8)) % 8
           )

    # 3次メッシュ
    def mesh_3rd(self):
        return (
            int(math.floor(self.lat*120 / 80)) * 1000000 + int(math.floor((self.lon-100))) * 10000 +
            int(math.floor(self.lat*120 % 80 / 10)) * 1000 + int(math.floor((self.lon-100) * 80 % 80 / 10)) * 100 +
            int(math.floor(self.lat*120 % 10)) * 10 + int(math.floor((self.lon-100) * 80)) % 10 
            )

    # 4次メッシュ
    def mesh_4th(self):  
        return (
            int(math.floor(self.lat*240 / 160)) * 10000000 + int(math.floor((self.lon-100)*160 / 160)) * 100000 +
            int(math.floor(self.lat*240 % 160 / 20)) * 10000 + int(math.floor((self.lon-100)*160 % 160 / 20)) * 1000 +
            int(math.floor(self.lat*240 % 20 / 2)) * 100 + int(math.floor((self.lon-100)*160 % 20 / 2)) * 10 +
            int(math.floor(self.lat*240)) % 2 * 2 + int(math.floor((self.lon-100)*160)) % 2 + 1
            )


if __name__ == "__main__":
    lon = 137.240625
    lat = 36.4979166666656
    print(PoinToMesh(lon, lat).mesh_4th())
    print(PoinToMesh(lon, lat).mesh_1st())
