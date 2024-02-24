from csv import reader
from datetime import datetime
from domain.aggregated_data import AggregatedData

class FileDatasource:
    def __init__(self, accelerometer_filename: str, gps_filename: str) -> None:
        self.accelerometer_filename = accelerometer_filename
        self.gps_filename = gps_filename
        self.accelerometer_file = None
        self.gps_file = None
    

    def startReading(self):
        self.accelerometer_file = open(self.accelerometer_filename, 'r')
        self.gps_file = open(self.gps_filename, 'r')
    

    def stopReading(self):
        if self.accelerometer_file:
            self.accelerometer_file.close()
        if self.gps_file:
            self.gps_file.close()


    def read(self) -> AggregatedData:
        if not (self.accelerometer_file and self.gps_file):
            raise ValueError("Files are not opened. Call startReading first.")

        accelerometer_data = self._read_csv(self.accelerometer_file)
        gps_data = self._read_csv(self.gps_file)
        time = datetime.now()

        return AggregatedData(accelerometer=accelerometer_data, gps=gps_data, time=time)
    

    def _read_csv(self, file) -> list:
        csv_reader = reader(file)
        return list(csv_reader)