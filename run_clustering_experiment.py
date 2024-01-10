import numpy as np
import matplotlib.pyplot as plt
# from scipy.stats import skew, kurtosis

from reinforce_trader.research.create_clustering_v1 import create_clustering_v1


hparams = {
    'data': {
        'tickers': ['GOOGL'],
        'window_size': 28,
    },
    'feature_pipeline': {
    },
    'data_splitter': {
        'test_size': 0.1,
        'gap_size': 14,
    },
    'model': {
        'n_clusters': 10,
        'init': 'k-means++',
        'n_init': 'auto',
        'max_iter': 300,
        'tol': 1e-4,
        'algorithm': 'lloyd',
        'random_state': 0
    }
}


def normalize_sequences(input_sequences: np.ndarray):
    # Extract the first timestep across all sequences for normalization
    first_timesteps = input_sequences[:, 0, 0]
    
    # Perform the log transformation and normalization in a vectorized manner
    transformed_sequences = np.log(input_sequences[:, :, 0]) - np.log(first_timesteps)[:, None]
    
    # Reshape the output to add the third dimension back
    return transformed_sequences[..., np.newaxis]

# def transform_sequences(input_sequences):
#     """
#     Transform sequences based on their shape features.
    
#     Parameters:
#     input_sequences (numpy.ndarray): A 3D array of price sequences (shape: N x number_of_steps x 1)
    
#     Returns:
#     numpy.ndarray: Transformed sequences with the same shape as input.
#     """
#     num_sequences, num_steps, _ = input_sequences.shape
#     transformed_sequences = []

#     # Iterate over each sequence
#     for i in range(num_sequences):
#         seq = input_sequences[i, :, 0]  # Extract the sequence as 1D array
#         # seq = np.log(seq) - np.log(seq[0])
#         # Calculate various statistical features
#         mean_price = np.mean(seq)
#         max_price = np.max(seq)
#         min_price = np.min(seq)
#         std_dev = np.std(seq)
#         price_range = max_price - min_price
#         price_skewness = skew(seq)
#         price_kurtosis = kurtosis(seq)
#         price_change = seq[-1] - seq[0]

#         # Combine the features into a single value for this sequence
#         combined_feature = (mean_price, max_price, min_price, std_dev, price_range, price_skewness, price_kurtosis, price_change)

#         # Assign this combined feature value across all steps for this sequence
#         transformed_sequences.append(np.array(combined_feature).reshape(len(combined_feature), 1))

#     return np.array(transformed_sequences)


def main():
    k = hparams['model']['n_clusters']
    trainer = create_clustering_v1(hparams)
    
    model, _ = trainer.train(to_analyst=False)
    features, _ = trainer.get_data('train')

    labels = model.predict(features)

    # Plotting the sequences in subplots for each cluster
    fig, axes = plt.subplots(k, 1, figsize=(10, 6 * k))

    for i, ax in enumerate(axes):
        cluster_indices = np.where(labels == i)[0]
        print(f"Cluster {i} has {len(cluster_indices)} sequences.")  # Debugging line

        if len(cluster_indices) == 0:
            ax.set_title(f'Cluster {i} (Empty)')
            continue

        subset_indices = cluster_indices[:10]  # Plot up to 10 sequences per cluster
        for index in subset_indices:
            ax.plot(features[index, :], label=f'Sequence {index}')
            ax.legend()

        ax.set_title(f'Cluster {i}')
        ax.set_xlabel('Time Steps')
        ax.set_ylabel('Sequence Value')

    plt.tight_layout()
    plt.show()
    # Dictionary to store cluster statistics
    # cluster_stats = {}

    # for i in range(k):
    #     cluster_indices = np.where(labels == i)[0]
    #     cluster_features = features[cluster_indices]

    #     # Calculating statistics for each feature across the cluster
    #     mean_cluster_features = np.mean(cluster_features, axis=0)
    #     std_cluster_features = np.std(cluster_features, axis=0)
    #     min_cluster_features = np.min(cluster_features, axis=0)
    #     max_cluster_features = np.max(cluster_features, axis=0)
    #     skewness_cluster_features = skew(cluster_features, axis=0)
    #     kurtosis_cluster_features = kurtosis(cluster_features, axis=0)

    #     # Storing in dictionary
    #     cluster_stats[i] = {
    #         'mean': mean_cluster_features,
    #         'std': std_cluster_features,
    #         'min': min_cluster_features,
    #         'max': max_cluster_features,
    #         'skewness': skewness_cluster_features,
    #         'kurtosis': kurtosis_cluster_features
    #     }

    #     # Print or return cluster_stats as needed
    #     for cluster, stats in cluster_stats.items():
    #         print(f"Cluster {cluster}:")
    #         for stat_name, stat_values in stats.items():
    #             print(f"  {stat_name}: {stat_values}")
    #         print()


if __name__ == '__main__':
    main()
