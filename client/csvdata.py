import csv
import config


class PvTables:
    def __init__(self):
        pv_path_dict = config.PV['path']
        self.pv_location = pv_path_dict['location']
        self.pv_latest = pv_path_dict['stored']['latest']
        self.pv_030 = pv_path_dict['stored']['030']
        self.pv_060 = pv_path_dict['stored']['060']
        self.pv_090 = pv_path_dict['stored']['090']
        self.pv_120 = pv_path_dict['stored']['120']
        self.pv_150 = pv_path_dict['stored']['150']
        self.pv_180 = pv_path_dict['stored']['180']

    def location(self):
        with open(self.pv_location, 'r') as f:
            reader = csv.reader(f)
            location_table = [li for li in reader]
            return location_table

    def stored(self, specified_time):
        if specified_time == 'latest':
            pv_stored_file = self.pv_latest
        elif specified_time == 30:
            pv_stored_file = self.pv_030
        elif specified_time == 60:
            pv_stored_file = self.pv_060
        elif specified_time == 90:
            pv_stored_file = self.pv_090
        elif specified_time == 120:
            pv_stored_file = self.pv_120
        elif specified_time == 150:
            pv_stored_file = self.pv_150
        elif specified_time == 180:
            pv_stored_file = self.pv_180
        with open(pv_stored_file, 'r') as f:
            reader = csv.reader(f)
            store_table = [li for li in reader]
        return store_table


class ConsumeTables:
    def __init__(self):
        consume_path_dict = config.CONSUME['path']
        self.consume_location = consume_path_dict['location']
        self.consume_latest = consume_path_dict['consume']['latest']
        self.consume_030 = consume_path_dict['consume']['030']
        self.consume_060 = consume_path_dict['consume']['060']
        self.consume_090 = consume_path_dict['consume']['090']
        self.consume_120 = consume_path_dict['consume']['120']
        self.consume_150 = consume_path_dict['consume']['150']
        self.consume_180 = consume_path_dict['consume']['180']

    def location(self):
        with open(self.consume_location, 'r') as f:
            reader = csv.reader(f)
            consume_table = [li for li in reader]
        return consume_table

    def consume(self, specified_time):
        # specified_time is ('latest' or 30 or 60 or 90 or 120 or 150 or 180)
        if specified_time == 'latest':
            consume_file = self.consume_latest
        elif specified_time == 30:
            consume_file = self.consume_030
        elif specified_time == 60:
            consume_file = self.consume_060
        elif specified_time == 90:
            consume_file = self.consume_090
        elif specified_time == 120:
            consume_file = self.consume_120
        elif specified_time == 150:
            consume_file = self.consume_150
        elif specified_time == 180:
            consume_file = self.consume_180
        with open(consume_file, 'r') as f:
            reader = csv.reader(f)
            store_table = [li for li in reader]
        return store_table

    def tests(self):
        self.tables = self.consume('latest')
        tab = self.tables[0]
        return tab


if __name__ == '__main__':
    t = PvTables()
    print(t.stored(30)[1])
    print(len(t.location()))
    c = ConsumeTables()
    print(c.consume(30)[1])
    print(len(c.location()))


