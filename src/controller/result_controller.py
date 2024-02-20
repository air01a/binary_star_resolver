import numpy as np

class ResultController:

    def __init__(self, sampling):
        self.results = {}
        self.sampling = sampling


    def add_result(self, name, type, result):
        result = result * self.sampling
        self.results[name]={'type':type, 'value': result}
        return result

    def get_results(self, name):
        if not name in self.results.keys():
            return None
        return self.results[name]

    def populate_result(self):
        average, sigma = self.get_stats()
        for k in self.results.keys():
            self.results[k]['ecart']=abs(self.results[k]['value']-average)
        

    def get_stats(self):
        values = np.array([ self.results[k]['value'] for k in self.results.keys()])
        average = values.mean()
        sigma = values.std()
        return average, sigma
    
    def print_result(self):
        for k in self.results.keys():
            print(f"{k} ({self.results[k]['type']}) : {self.results[k]['value']} ( { self.results[k]['ecart'] })")
        a,s = self.get_stats()
        print("---------------")
        print(f"Average={a:.2f}")
        print(f"Std={s:.2f}")



        

