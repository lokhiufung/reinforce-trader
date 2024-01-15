from reinforce_trader.research.get_sequences import get_rolling_window_sequences
from reinforce_trader.research.data_splitters.gapped_data_splitter import gapped_cv_data_splitter, gapped_data_splitter


class Dataset:
        def __init__(self, df):
            self.df = df
            # self.data_splitter = data_splitter
            self.partitions = {}
            self.partitions_k_fold = []

        def create_partitions(self, test_size: float, window_size: int, gap_size: int, feature_len: int) -> 'Dataset':
            # turn df to array
            array = get_rolling_window_sequences(self.df, window_size=window_size)
            array_splitted = gapped_data_splitter(array, test_size=test_size, gap_size=gap_size)

            for partition_name, array in array_splitted.items():
                self.partitions[partition_name] = {}
                # drop the last axis
                feature = array_splitted['train'][:, :feature_len, :]
                target = array_splitted['train'][:, feature_len:, :]
                
                self.partitions[partition_name]['feature'] = feature
                self.partitions[partition_name]['target'] = target
        
            return self
        
        def create_k_fold_partitions(self, num_folds: int, test_size: float, window_size: int, gap_size: int, feature_len: int) -> 'Dataset':
            # turn df to array
            array = get_rolling_window_sequences(self.df, window_size=window_size)
            array_splitted_k_fold = gapped_cv_data_splitter(array, num_folds, test_size=test_size, gap_size=gap_size)

            for array_splitted in array_splitted_k_fold:
                partitions = {}
                for partition_name, array in array_splitted.items():
                    self.partitions[partition_name] = {}
                    # drop the last axis
                    feature = array_splitted['train'][:, :feature_len, :]
                    target = array_splitted['train'][:, feature_len:, :]
                    
                    partitions[partition_name]['feature'] = feature
                    partitions[partition_name]['target'] = target
                self.partitions_k_fold.append(partitions)

            return self
        
        def get_partition(self, partition_name, array_name, transformation=None, fold_index=None):
            if not fold_index:
                dataset =  self.partitions[partition_name][array_name]
            else:
                dataset = self.partitions_k_fold[fold_index][partition_name][array_name]
            
            # transformation
            if transformation is not None:
                dataset = transformation(dataset)
            return dataset

        @property 
        def num_folds(self):
            return len(self.partitions_k_fold)
    
        

