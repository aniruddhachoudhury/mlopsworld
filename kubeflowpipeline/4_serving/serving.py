import os
import sys
import json 
import kfserving   
import numpy as np 
import pandas as pd
import tensorflow as tf 
from typing import List, Dict
from sklearn.preprocessing import StandardScaler



class taxiclassifier(kfserving.KFModel):

    def __init__(self, name: str):
        super().__init__(name)
        self.name = name
        self.ready = False
        self.gspath = os.environ["STORAGE_URI"]

    def load(self):
        model = tf.keras.models.load_model(self.gspath)
        self.model = model
        self.ready = True

    def predict(self, request: Dict) -> Dict:
        scaler = StandardScaler()
        inputs = scaler.fit_transform(pd.DataFrame(request["instances"])) 
        reshaped_to_2d = np.reshape(inputs, (-1, len(inputs)))
        results = self.model.predict(reshaped_to_2d)
        result = (results > 0.45)*1 
        if int(result)==1:
            result="Profit of Driver"
        else:
            result="Loss of Driver"
        print("result : {0}".format(result))
        return {"predictions": result}


if __name__ == "__main__":
    model = taxiclassifier("feature-serving")
    model.load()
    kfserving.KFServer(workers=1).start([model])
        
