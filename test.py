import pandas as pd
from config.paths import PRODUCT_XLSX

def clean_product_table():
    # Load Excel
    df = pd.read_excel(PRODUCT_XLSX)

    # Normalize column names
    df.columns = df.columns.str.strip().str.title()
    print("Columns found in file:", df.columns.tolist())

    # Keep only relevant columns
    required_cols = ['Type', 'Item Description', 'Material']
    for c in required_cols:
        if c not in df.columns:
            raise ValueError(f"Missing column: {c}")

    product_df = df[required_cols].copy()

    # Clean text: strip and title case
    product_df['Type'] = product_df['Type'].astype(str).str.strip().str.title()
    product_df['Material'] = product_df['Material'].astype(str).str.strip().str.title()
    product_df['Item Description'] = product_df['Item Description'].astype(str).str.strip()

    # Remove duplicates first
    product_df = product_df.drop_duplicates().reset_index(drop=True)

    # Split Item Description into parts by comma
    def parse_description(desc):
        parts = [p.strip() for p in desc.split(',')]
        color = pattern = neck = other = ""

        for p in parts:
            low = p.lower()
            # Identify Color
            if any(c in low for c in ['green', 'red', 'blue', 'yellow', 'black', 'white', 'sea', 'pink']):
                color = p if color == "" else color + "; " + p
            # Identify Neck Style
            elif 'neck' in low:
                neck = p if neck == "" else neck + "; " + p
            # Identify Pattern / Design
            elif any(k in low for k in ['flower', 'print', 'pattern', 'stripe', 'polka']):
                pattern = p if pattern == "" else pattern + "; " + p
            # Other details
            else:
                other = p if other == "" else other + "; " + p

        return pd.Series([color, pattern, neck, other])

    product_df[['Color', 'Pattern', 'Neck Style', 'Other Details']] = product_df['Item Description'].apply(parse_description)

    # Optional: drop original Item Description if you want structured table only
    # product_df = product_df.drop(columns=['Item Description'])

    return product_df

if __name__ == "__main__":
    clean_df = clean_product_table()
    print(clean_df.head(10))
    clean_df.to_csv('clean_product_table.csv', index=False)
    print("Clean product table saved to 'clean_product_table.csv'")