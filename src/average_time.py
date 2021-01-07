from datetime import datetime

class AverageTime:
    '''
    This class calculates the average scraping time per paper.
    '''

    def current_timestamp(self):
        '''
        Returns a timestamp in UTC.
        '''

        return datetime.utcnow()

    def subtract(self, start, end):
        '''
        Subtract the end timestamp with the start timestamp.
        '''

        return (end - start).total_seconds()
    
    def result(self, timestamp):
        '''
        Prints the average scraping time for each paper in second.
        '''
        timestamp = round((sum(timestamp) / len(timestamp)), 3) if timestamp != [] else 0
        print(f'On average, the operation takes {timestamp} second(s).')