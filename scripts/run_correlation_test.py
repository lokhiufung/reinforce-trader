import pandas as pd
from scipy.stats import pearsonr


def run_correlation_test():
    # Load the labels data
    labels_path = './data/charts/labels.csv'  # Replace with your file path
    labels_df = pd.read_csv(labels_path, header=None, names=['Chart', 'Label'])

    # Calculate the lagged labels
    labels_df['Lagged_Label'] = labels_df['Label'].shift(1)

    # Drop NaN values created by the lag
    labels_df.dropna(inplace=True)

    # Calculate the Pearson correlation coefficient and the p-value
    correlation, p_value = pearsonr(labels_df['Label'], labels_df['Lagged_Label'])

    # Output the results
    print(f"Correlation Coefficient: {correlation}")
    print(f"P-value: {p_value}")

    # Hypothesis testing
    alpha = 0.05  # Significance level
    if p_value < alpha:
        print("Reject the null hypothesis - there is significant serial correlation.")
    else:
        print("Fail to reject the null hypothesis - there is no significant serial correlation.")



if __name__ == '__main__':
    run_correlation_test()