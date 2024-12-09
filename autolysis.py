# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests",
#   "pandas",
#   "seaborn",
#   "matplotlib",
# ]
# ///

import os
import sys
import json
import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from typing import Dict, Any

os.environ["AIPROXY_TOKEN"] = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjIwMDIzNjRAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.Z4Jf0iLBOMYYjUHUyL3ZipWrrUL1NVsDL4Ko-rxsSfE"

class AutomatedAnalysis:
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.df = pd.read_csv(dataset_path, encoding='latin-1')
        self.ai_proxy_token = os.environ.get("AIPROXY_TOKEN")
        if not self.ai_proxy_token:
            raise ValueError("AIPROXY_TOKEN environment variable not set")
        
        self.base_url = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"

    def analyze_dataset(self) -> Dict[str, Any]:
        analysis = {
            "dataset_info": {
                "rows": len(self.df),
                "columns": list(self.df.columns),
                "column_types": {col: str(dtype) for col, dtype in self.df.dtypes.items()},
                "missing_values": self.df.isnull().sum().to_dict(),
                "sample_data": self.df.head().to_dict()
            }
        }
        return analysis

    def generate_visualizations(self, analysis_results: Dict[str, Any]):
        plt.figure(figsize=(20, 20))
        
        # Correlation heatmap
        numeric_columns = self.df.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_columns) > 1:
            plt.subplot(1, 2, 1)
            correlation_matrix = self.df[numeric_columns].corr()
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5)
            plt.title('Correlation Heatmap')
            plt.tight_layout()
            plt.savefig('correlation_heatmap.png')
            plt.close()

        # Distribution of numeric columns
        plt.figure(figsize=(10, 6))
        numeric_columns = [col for col in numeric_columns if len(self.df[col].dropna()) > 0]
        for i, col in enumerate(numeric_columns[:3], 1):
            plt.subplot(1, 3, i)
            sns.histplot(self.df[col].dropna(), kde=True)
            plt.title(f'Distribution of {col}')
        plt.tight_layout()
        plt.savefig('numeric_distributions.png')
        plt.close()

    def generate_story(self, analysis_results: Dict[str, Any]) -> str:
        prompt = f"""
        Write a narrative about this dataset analysis. Include:
        1. Dataset description
        2. Key insights
        3. Potential implications
        4. Use Markdown formatting

        Dataset Details:
        {json.dumps(analysis_results['dataset_info'], indent=2)}
        """

    
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}]
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.ai_proxy_token}"
        }

        try:
            print("Requesting response...")
            response = requests.post(self.base_url, headers=headers, json=payload)

            
            if response.status_code == 200:
                data = response.json()
                print("Response received!")
                print(f"Full Response: {data}")
                return data.get('choices', [{}])[0].get('message', {}).get('content', 'No message content available')
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return f"Error generating response: {response.status_code}"

        except Exception as e:
            print("Error encountered!")
            print(f"Error details: {e}")
            return f"Error generating response: {str(e)}"

    def run(self):
        analysis_results = self.analyze_dataset()
        self.generate_visualizations(analysis_results)
        
        story = self.generate_story(analysis_results)
        
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(story)

def main():
    if len(sys.argv) != 2:
        print("Usage: uv run autolysis.py <dataset.csv>")
        sys.exit(1)
    
    dataset_path = sys.argv[1]
    analysis = AutomatedAnalysis(dataset_path)
    analysis.run()

if __name__ == "__main__":
    main()
