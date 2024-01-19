# TODO: refactor the code
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from scipy.signal import argrelextrema
from scipy.stats import entropy

from reinforce_trader.research.metrics.codependency import get_normalized_conditional_entropy
from reinforce_trader.research.features.standardizing_feature import get_minmax_scaling


def find_pips(price_sequence, order=1):
    """
    Identify Perceptually Important Points (PIPs) in a price sequence.
    
    Parameters:
    - price_sequence: A numpy array of prices.
    - order: How many points on each side to use for the comparison to find extrema.
    
    Returns:
    - A numpy array of indices representing the PIPs.
    """
    # Always include the first and the last points
    pips = [0, len(price_sequence) - 1]
    
    # Find local maxima and minima
    local_maxima = argrelextrema(price_sequence, np.greater, order=order)[0].tolist()
    local_minima = argrelextrema(price_sequence, np.less, order=order)[0].tolist()
    
    # Combine and sort the indices of the PIPs
    pips.extend(local_maxima)
    pips.extend(local_minima)
    pips = sorted(set(pips))  # Remove duplicates and sort
    
    return np.array(pips)


def plot_pip_sequence(price_sequence):
    pip_indexes = find_pips(price_sequence)
    pip_values = price_sequence[pip_indexes]

    # Plot the original price sequence
    plt.figure(figsize=(14, 7))
    plt.subplot(2, 1, 1)
    plt.plot(price_sequence, linestyle='-', marker='o', color='green', markersize=4, label='Original Price Sequence')
    plt.title('Context Scale Time Series')
    plt.xlabel('Time Steps')
    plt.ylabel('Price')
    plt.legend()

    # Plot the PIPs
    plt.subplot(2, 1, 2)
    plt.plot(pip_indexes, pip_values, linestyle='-', marker='o', color='red', markersize=6, label='Perceptually Important Points')
    plt.title('Most Important Point of Context Scale Time Series')
    plt.xlabel('Points')
    plt.ylabel('Price')
    plt.legend()

    plt.tight_layout()
    plt.show()


def plot_conditional_distribution(labels_long, labels_short):
    # Determine the unique clusters in labels_long
    unique_clusters = np.unique(labels_long)

    # Create subplots - one histogram for each cluster in labels_long
    n_rows = len(unique_clusters) // 3 + (len(unique_clusters) % 3 > 0)
    fig, axes = plt.subplots(n_rows, 3, figsize=(15, 5 * n_rows))

    for i, cluster in enumerate(unique_clusters):
        ax = axes.flatten()[i]
        # Filter labels_short based on the current cluster in labels_long
        labels_short_in_cluster = labels_short[labels_long == cluster]
        ax.hist(labels_short_in_cluster, bins=len(unique_clusters), edgecolor='black')
        ax.set_title(f'Histogram for labels_short given labels_long = {cluster}')
        ax.set_xlabel('labels_short')
        ax.set_ylabel('Frequency')

    # Hide any unused subplots
    for i in range(len(unique_clusters), len(axes.flatten())):
        axes.flatten()[i].set_visible(False)

    # Adjust the layout
    plt.tight_layout()
    plt.show()


def generate_random_labels(num_unique, size=100):
    """Generate a random sequence of labels."""
    return np.random.randint(0, num_unique, size=size)


def plot_normalized_conditional_entropy_for_random_labels():
    # Number of unique labels to test
    num_unique_labels = range(2, 31)  # From 2 to 30 unique labels

    # List to store calculated entropies
    normalized_entropies = []

    # Calculating normalized conditional entropy for different numbers of unique labels
    for num in num_unique_labels:
        labels_1 = generate_random_labels(num)
        labels_2 = generate_random_labels(num)
        nce = get_normalized_conditional_entropy(labels_1, labels_2)
        normalized_entropies.append(nce)

    # Plotting the results
    plt.figure(figsize=(10, 6))
    plt.plot(num_unique_labels, normalized_entropies, marker='o')
    plt.xlabel('Number of Unique Labels')
    plt.ylabel('Normalized Conditional Entropy')
    plt.title('Normalized Conditional Entropy vs. Number of Unique Labels')
    plt.grid(True)
    plt.show()


def plot_dct_and_dct_reconstruction(time_series, time_series_dct, reconstructed_signal):
# Plotting the original and reconstructed signals
    plt.figure(figsize=(18, 5))

    # Original Signal Plot
    plt.subplot(1, 3, 1)
    plt.plot(time_series, label='Original Signal')
    plt.title('Original signal (Min-Max Scaling)')
    plt.xlabel('Time (days)')
    plt.ylabel('Price scale')
    plt.legend()

    # DCT Coefficients Plot
    plt.subplot(1, 3, 2)
    plt.stem(time_series_dct, basefmt=" ")
    plt.title('Discrete Cosine Transform coefficients')
    plt.xlabel('Frequency Space (1/days)')
    plt.ylabel('Coefficient scale')
    plt.legend()

    # Reconstructed Signal Plot
    plt.subplot(1, 3, 3)
    plt.plot(reconstructed_signal, label='Reconstructed Signal')
    plt.title('Reconstructed signal using inverse DCT')
    plt.xlabel('Time (days)')
    plt.ylabel('Price scale')
    plt.legend()

    plt.tight_layout()
    plt.show()


def plot_random_forest_feature_importances(importances):
    indices = range(len(importances))

    # Sorting the feature importances in descending order
    sorted_indices = sorted(indices, key=lambda i: importances[i], reverse=True)
    print(f'top 10 features: {sorted_indices[:10]}')

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.title("Feature Importances in Random Forest Classifier")
    plt.bar(range(len(importances)), importances[sorted_indices], align='center')
    plt.xticks(range(len(importances)), sorted_indices)
    plt.xlabel("Feature Index")
    plt.ylabel("Importance")
    plt.show()


def plot_vi_distribution(df):
    plt.figure(figsize=(12, 6))
    plt.hist(df['metric'], bins=30, density=True, alpha=0.6, color='g')
    
    # Adding a line for the mean
    mean = df['metric'].mean()
    plt.axvline(mean, color='r', linestyle='dashed', linewidth=1)
    min_ylim, max_ylim = plt.ylim()
    plt.text(mean*1.01, max_ylim*0.9, f'Mean: {mean:.2f}')
    
    plt.title('Distribution of Variation of Information (VI) for SP500 Stock Pairs')
    plt.xlabel('Variation of Information')
    plt.ylabel('Density')
    plt.grid(True)
    plt.show()


def plot_clustered_sequences_with_plotly(k, labels, features, centroids):
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


def plot_clustered_sequences_with_matplotlib(k, labels, features, centroids):
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


def plot_elbow_and_silhouette(sse, silhouette_scores, db_index):
    plt.figure(figsize=(14, 7))
    
    plt.subplot(2, 2, 1)
    plt.plot(list(sse.keys()), list(sse.values()))
    plt.xlabel("Number of clusters")
    plt.ylabel("SSE")
    plt.title("Elbow Method")

    plt.subplot(2, 2, 2)
    plt.plot(list(silhouette_scores.keys()), list(silhouette_scores.values()))
    plt.xlabel("Number of clusters")
    plt.ylabel("Silhouette Score")
    plt.title("Silhouette Method")
    
    plt.subplot(2, 2, 3)
    plt.plot(list(db_index.keys()), list(db_index.values()))
    plt.xlabel("Number of clusters")
    plt.ylabel("Davies-Bouldin Index")
    plt.title("Davies-Bouldin Index")
    plt.gca().invert_yaxis()  # Invert y-axis as lower scores are better for Davies-Bouldin Index
    
    # plt.subplot(2, 2, 4)
    # plt.plot(list(gap_statistic.keys()), list(gap_statistic.values()))
    # plt.xlabel("Number of clusters")
    # plt.ylabel("Gap Statistic")
    # plt.title("Gap Statistic")
    # Note: Uncomment the above lines and implement the gap statistic calculation to use this
    
    plt.show()


def plot_feature_label_sequences(selected_features, selected_targets):
    selected_sequences = np.concatenate((selected_features, selected_targets), axis=1)
    selected_sequences = get_minmax_scaling(selected_sequences)
    selected_sequences = selected_sequences[:, :, 0]
    
    # Plotting
    fig = go.Figure()

    # Add each sequence to the plot
    for i, seq in enumerate(selected_sequences):
        fig.add_trace(go.Scatter(
            x=np.arange(seq.shape[0]), 
            y=seq, 
            mode='lines', 
            line=dict(width=1, color='purple'),  # Set line color to purple
            showlegend=False
        ))

    # Calculate and add the mean sequence (if that's what the yellow line represents)
    mean_sequence = np.mean(selected_sequences, axis=0)
    fig.add_trace(go.Scatter(
        x=np.arange(mean_sequence.shape[0]), 
        y=mean_sequence, 
        mode='lines', 
        line=dict(width=2, color='yellow'),  # Set line color to yellow
        name='Mean Sequence'
    ))

    # Add a vertical line at step 28
    fig.add_vline(x=28, line=dict(color='red', width=2, dash='dash'))

    # Update layout
    fig.update_layout(
        title='Price Sequences Visualization',
        xaxis_title='Time Step',
        yaxis_title='Price',
        template='plotly_white'
    )

    fig.show()