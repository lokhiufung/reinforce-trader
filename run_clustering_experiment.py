import numpy as np
# from scipy.stats import skew, kurtosis

from reinforce_trader.research.create_clustering_v1 import create_clustering_v1


hparams = {
    'data': {
        'tickers': ['GOOGL'],
        'window_size': 20,
    },
    'feature_pipeline': {
    },
    'data_splitter': {
        'test_size': 0.1,
        'gap_size': 14,
    },
    'model': {
        'n_clusters': 20,
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


def plot_with_matplotlib(k, labels, features, centroids):
    import matplotlib.pyplot as plt

    # Plotting the sequences in subplots for each cluster
    fig, axes = plt.subplots(k, 1, figsize=(15, 4 * k), sharex=True)
    
    if k == 1:  # If there's only one cluster, axes will not be an array
        axes = [axes]

    for i, ax in enumerate(axes):
        cluster_indices = np.where(labels == i)[0]
        print(f"Cluster {i} has {len(cluster_indices)} sequences.")  # Debugging line

        if len(cluster_indices) == 0:
            ax.set_title(f'Cluster {i} (Empty)')
            continue

        # Plot all sequences in the cluster
        for index in cluster_indices:
            ax.plot(features[index, :], color='blue', linewidth=0.5, alpha=0.1)

        # Plot the centroid with a more prominent line
        ax.plot(centroids[i], color='yellow', linewidth=2, label=f'Centroid {i}')
        ax.legend(loc='upper right')

        ax.set_title(f'Cluster {i} centroid (n={len(cluster_indices)})')
        ax.set_xlabel('Days')
        ax.set_ylabel('Normalized Value')

    plt.tight_layout()
    plt.show()


def plot_with_plotly(k, labels, features, centroids):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    # Create a subplot figure with k rows
    fig = make_subplots(rows=k, cols=1, shared_xaxes=True, vertical_spacing=0.02)

    for i in range(k):
        cluster_indices = np.where(labels == i)[0]
        
        # For each cluster, add a subplot with the sequences
        for index in cluster_indices:
            fig.add_trace(
                go.Scatter(
                    x=np.arange(features.shape[1]), 
                    y=features[index, :].flatten(), 
                    mode='lines',
                    line=dict(width=1, color='blue'),
                    opacity=0.1,  # Set opacity directly for the Scatter object
                    showlegend=False,
                    name=f'Cluster {i} Sequence'
                ),
                row=i+1, col=1
            )
        
        # Add the centroid with a more prominent line
        fig.add_trace(
            go.Scatter(
                x=np.arange(features.shape[1]), 
                y=centroids[i].flatten(), 
                mode='lines+markers',
                line=dict(width=2, color='yellow'),
                marker=dict(size=4),
                name=f'Cluster {i} Centroid'
            ),
            row=i+1, col=1
        )

    # Update layout for each subplot
    for i in range(k):
        fig.update_yaxes(title_text=f'Cluster {i}', row=i+1, col=1)

    # Update the layout of the figure
    fig.update_layout(
        title='Clusters and Centroids',
        xaxis_title='Days',
        height=300 * k,
        template='plotly_white',
        showlegend=False
    )

    fig.show()


def main():
    model_ckpt_dir = './model_ckpts/kmeans-20'

    k = hparams['model']['n_clusters']
    trainer = create_clustering_v1(hparams)
    
    model, _ = trainer.train(to_analyst=False)

    trainer.save(model_ckpt_dir)
    # features, _ = trainer.get_data('train')

    # labels = model.predict(features)

    #  # Get centroids
    # centroids = model.cluster_centers_

    # plot_with_plotly(k, labels, features, centroids)

    
if __name__ == '__main__':
    main()
