from dotenv import load_dotenv
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_groq import ChatGroq
import pandas as pd
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate

def categorize_transactions(df):
    
    load_dotenv()

    model = ChatGroq(
        model="deepseek-r1-distill-llama-70b",
        # model="gemma2-9b-it",
        temperature=1,
        max_tokens=None,
        timeout=None,
        max_retries=2
    )

    ### Categorise bank transactions with LLM
    categories_and_descriptions = [("Housing", "This includes your mortgage/rent, property taxes, homeowner insurance, and HOA fees"),
                ("Utilities", "Your gas, electricity, water, trash removal, and internet bills all fall under utilities"),
                ("Transportation", "Car payments, gas, public transportation, car insurance, parking costs"),
                ("Healthcare",  "Medical expenses, insurance premiums, copays, and prescription costs"),
                ("Food", "Groceries, dining out, coffee shop purchases"),
                ("Personal Care", "Personal hygiene items, haircuts, beauty products, gym memberships"),
                ("Debt Payments", "student loans, personal loans, etc."),
                ("Savings and Investments", "Effort to manage money for the future"),
                ("Shopping and Entertainment", "Clothing, electronics, entertainment, movies, concerts, subscription services, streaming"),
                ("Education and Professional Development", "Tuition, fees, supplies, books, and course materials, conferences, industry courses, software subscriptions, etc."),
                ("Taxes", "Includes all tax-related expenditures you’ve made (non-refundable promoters, etc.)"),
                ("Travel & Vacations", " Be generous with this if you're a travel enthusiast!")
                ]

    categories = [cat for (cat, dec) in categories_and_descriptions]
    descriptions = [dec for (cat, dec) in categories_and_descriptions]

    comb = "\n".join([f"{i+1}. {cat}: {dec} \n" for (i, (cat, dec)) in enumerate(categories_and_descriptions)])

    class Transaction(BaseModel):
        category: Literal['Housing', 'Utilities','Transportation','Healthcare','Food',
                        'Personal Care','Debt Payments','Savings and Investments','Shopping and Entertainment',
                            'Education and Professional Development','Taxes','Travel & Vacations'] = Field(description="choose best category for the given bank transaction out of the following categories: " + "; ".join(categories))
        
    parser = PydanticOutputParser(pydantic_object=Transaction)

    prompt = ChatPromptTemplate([
        ('system', 'You are a personal assistant whose job is to categorise given personal bank transactions by choosing the best fitting category from one of the following categories : \n\n' + comb),
        ('human', 'Transaction details: {query}; \n {format_instructions}')
    ])


    categories = []

    for i in range(len(df)):
        transaction = "; ".join([str(x) for x in list(df.iloc[i].values)])
        chain = prompt | model | parser
        categories.append(chain.invoke({'query': transaction, 'format_instructions': parser.get_format_instructions()}))
    
    categories = [x.category for x in categories]
    
    categories_df = df.copy()
    categories_df["category"] = categories

    categories_df.to_csv("transactions_2022_2023_categorized.csv", index=False)
    
    return categories_df

