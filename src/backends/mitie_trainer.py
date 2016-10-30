from mitie import *
import os
import datetime
import json


class MITIETrainer(object):
    def __init__(self,config):
        self.name="mitie"
        self.training_data = None
        self.intent_classifier = None
        self.entity_extractor = None
        self.training_data = None
        self.fe_file = config["fe_file"]
    
    def train(self,data):
        self.training_data = data
        self.intent_classifier = self.train_intent_classifier(data.intent_examples)
        self.entity_extractor = self.train_entity_extractor(data.entity_examples)

    def start_and_end(self,text_tokens,entity_tokens):
        print(text_tokens)
        print(entity_tokens)
        size = len(entity_tokens)
        max_loc = 1+len(text_tokens)-size
        #print(shift)
        #print(max_loc)
        for i in range(max_loc):
            print(text_tokens[i:i+size])
            
        locs = [ i for i in range(max_loc) if \
                 text_tokens[i:i+size] == entity_tokens ]
        print(locs)
        start, end = locs[0], locs[0]+len(entity_tokens)        
        return start, end
                
    def train_entity_extractor(self,entity_examples):
        trainer = ner_trainer(self.fe_file)
        for example in entity_examples:        
            print(example)
            tokens = tokenize(example["text"])
            sample = ner_training_instance(tokens)
            for ent in example["entities"]:
                _slice = example["text"][ent["start"]:ent["end"]]
                print(_slice)
                val_tokens = tokenize(_slice)
                start, end = self.start_and_end(tokens,val_tokens)
                sample.add_entity(xrange(start,end),ent["entity"])
            trainer.add(sample)
            
        ner = trainer.train()
        return ner
    
    def train_intent_classifier(self,intent_examples):
        trainer = text_categorizer_trainer(self.fe_file)
        for example in intent_examples:
            tokens = tokenize(example["text"])
            trainer.add_labeled_text(tokens,example["intent"])   
                     
        intent_classifier = trainer.train()
        return intent_classifier

        
    def persist(self,path):
        tstamp = datetime.datetime.now().strftime('%Y%m%d-%H%M')
        dirname = os.path.join(path,"model_"+tstamp)
        os.mkdir(dirname)
        data_file = os.path.join(dirname,"training_data.json")
        classifier_file = os.path.join(dirname,"intent_classifier.dat")
        entity_extractor_file = os.path.join(dirname,"entity_extractor.dat")
        
        metadata = {
          "trained_at":tstamp,
          "training_data":data_file,
          "backend":self.name,
          "intent_classifier":classifier_file,
          "entity_extractor": entity_extractor_file
        }
        
        with open(os.path.join(dirname,'metadata.json'),'w') as f:
            f.write(json.dumps(metadata,indent=4))
        with open(data_file,'w') as f:
            f.write(self.training_data.as_json(indent=2))

        self.intent_classifier.save_to_disk(classifier_file)
        self.entity_extractor.save_to_disk(entity_extractor_file)
        
        
        
        
        