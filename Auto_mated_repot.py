import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import os


def load_and_analyze_data(data: pd.DataFrame) -> pd.DataFrame:
    data['Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d')
    data['Total'] = data['Quantity'] * data['Price']
    monthly_sales = data.groupby([data['Date'].dt.to_period('M'), 'Product']).agg({
        'Quantity': 'sum',
        'Price': 'mean',
        'Total': 'sum'
    }).reset_index()
    return monthly_sales


def create_visualizations(monthly_sales: pd.DataFrame) -> None:
    plt.figure(figsize=(12, 8))
    
    
    pivot_data = monthly_sales.pivot(index='Date', columns='Product', values='Total')
    pivot_data.plot(kind='bar', stacked=False, ax=plt.gca())

    plt.title('Monthly Sales Report')
    plt.xlabel('Month')
    plt.ylabel('Total Sales')
    plt.legend(title='Product')
    plt.grid(True)
    plt.savefig('sales_report_chart.png')
    plt.close()


class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Monthly Sales Report', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title: str):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(10)

    def chapter_body(self, body: str):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

    def table(self, data: pd.DataFrame):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Sales Summary:', 0, 1)
        self.set_font('Arial', 'B', 10)
        
        col_widths = [30, 50, 30, 30]
        col_names = ['Date', 'Product', 'Quantity', 'Total']

        for col_name, col_width in zip(col_names, col_widths):
            self.cell(col_width, 10, col_name, 1)
        self.ln()

        self.set_font('Arial', '', 10)
        for row in data.itertuples(index=False):
            self.cell(col_widths[0], 10, str(row.Date), 1)
            self.cell(col_widths[1], 10, row.Product, 1)
            self.cell(col_widths[2], 10, str(row.Quantity), 1)
            self.cell(col_widths[3], 10, f'{row.Total:.2f}', 1)
            self.ln()

def generate_pdf_report(monthly_sales: pd.DataFrame) -> None:
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Monthly Sales Report', 0, 1, 'C')
    pdf.table(monthly_sales)
    pdf.add_page()
    pdf.chapter_title('Sales Chart')
    pdf.image('sales_report_chart.png', x=10, y=None, w=190)
    pdf_file_name = 'monthly_sales_report.pdf'
    pdf.output(pdf_file_name)
    print(f"PDF report generated successfully. Saved as: {pdf_file_name}")


def parse_text_file(file_path: str) -> pd.DataFrame:
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        
        header = lines[0].strip().split(',')
        data = []
        for line_num, line in enumerate(lines[1:], 2):  
            parts = line.strip().split(',')
            if len(parts) == 4:
                date, product, quantity, price = parts
                data.append([date, product, int(quantity), float(price)])
            else:
                print(f"Skipping improperly formatted line: {line_num} {line.strip()}")

        df = pd.DataFrame(data, columns=header)
        return df

    except Exception as e:
        print(f"An error occurred while reading the text file: {e}")
        return pd.DataFrame()

#
def run_report_generation(file_path: str) -> None:
    try:
        print("Current working directory:", os.getcwd())
        print("Absolute path to the text file:", os.path.abspath(file_path))
        data = parse_text_file(file_path)
        if not data.empty:
            monthly_sales = load_and_analyze_data(data)
            create_visualizations(monthly_sales)
            generate_pdf_report(monthly_sales)
    except FileNotFoundError:
        print(f"File not found: {file_path}. Please enter a valid file path.")
    except Exception as e:
        print(f"An error occurred: {e}")


def display_menu() -> None:
    print("Generate Monthly Sales Report")
    print("-----------------------------")
    print("Please provide the path to the text file containing sales data.")
    print("Enter 'exit' to quit.")

def main() -> None:
    while True:
        display_menu()
        file_path = input("Enter the path to the text file: ")

        if file_path.lower() == 'exit':
            print("Exiting...")
            break
        elif not os.path.exists(file_path):
            print("File not found. Please enter a valid file path.")
            continue
        else:
            run_report_generation(file_path)

if __name__ == "__main__":
    main()
