"""
Google Sheets Integration Module
Handles writing data to Google Sheets
"""

import os
import pickle
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# If modifying these scopes, delete the token.pickle file
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


class GoogleSheetsWriter:
    """
    Write data to Google Sheets
    """
    
    def __init__(self, credentials_path: str = "config/credentials.json", token_path: str = "config/token.pickle"):
        """
        Initialize Google Sheets writer
        
        Args:
            credentials_path: Path to Google API credentials JSON file
            token_path: Path to store authentication token
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API"""
        creds = None
        
        # Load token if it exists
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If credentials are invalid or don't exist, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            elif os.path.exists(self.credentials_path):
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            else:
                raise FileNotFoundError(
                    f"Credentials file not found at {self.credentials_path}. "
                    "Please download credentials from Google Cloud Console."
                )
            
            # Save credentials for next run
            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('sheets', 'v4', credentials=creds)
    
    def create_spreadsheet(self, title: str) -> str:
        """
        Create a new spreadsheet
        
        Args:
            title: Title of the spreadsheet
            
        Returns:
            Spreadsheet ID
        """
        try:
            spreadsheet = {
                'properties': {
                    'title': title
                }
            }
            
            result = self.service.spreadsheets().create(
                body=spreadsheet,
                fields='spreadsheetId'
            ).execute()
            
            return result.get('spreadsheetId')
        
        except HttpError as err:
            print(f"An error occurred: {err}")
            raise
    
    def setup_headers(self, spreadsheet_id: str, sheet_name: str = "Sheet1"):
        """
        Set up the standard headers for unit management table
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            sheet_name: Name of the sheet
        """
        headers = [
            ['차수 (Comma/Session)', '대단원 (Major Unit)', '소주제/테마 (Subtopic/Theme)', 
             '페이지 범위 (Page Range)', '학습 목표 및 튜터 코칭 포인트 (Learning Goals and Tutor Coaching Points)',
             '숙제 (Homework)', '체크 테스트 (Check Test)', '날짜 (Date)', '완료 상태 (Completion Status)']
        ]
        
        try:
            # Write headers
            self.write_data(spreadsheet_id, f"{sheet_name}!A1:I1", headers)
            
            # Format headers (bold, background color)
            requests = [
                {
                    'repeatCell': {
                        'range': {
                            'sheetId': 0,
                            'startRowIndex': 0,
                            'endRowIndex': 1
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {
                                    'red': 0.9,
                                    'green': 0.9,
                                    'blue': 0.9
                                },
                                'textFormat': {
                                    'bold': True
                                }
                            }
                        },
                        'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                    }
                }
            ]
            
            body = {'requests': requests}
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            
        except HttpError as err:
            print(f"An error occurred: {err}")
            raise
    
    def write_data(self, spreadsheet_id: str, range_name: str, values: List[List]):
        """
        Write data to spreadsheet
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            range_name: A1 notation range (e.g., 'Sheet1!A2:I2')
            values: 2D list of values to write
        """
        try:
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            return result
        
        except HttpError as err:
            print(f"An error occurred: {err}")
            raise
    
    def append_row(self, spreadsheet_id: str, sheet_name: str, row_data: List):
        """
        Append a row to the spreadsheet
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            sheet_name: Name of the sheet
            row_data: List of values for the row
        """
        try:
            body = {
                'values': [row_data]
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A:I",
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            return result
        
        except HttpError as err:
            print(f"An error occurred: {err}")
            raise
    
    def batch_append_rows(self, spreadsheet_id: str, sheet_name: str, rows_data: List[List]):
        """
        Append multiple rows to the spreadsheet
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            sheet_name: Name of the sheet
            rows_data: List of rows, where each row is a list of values
        """
        try:
            body = {
                'values': rows_data
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A:I",
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            return result
        
        except HttpError as err:
            print(f"An error occurred: {err}")
            raise
    
    def get_spreadsheet_url(self, spreadsheet_id: str) -> str:
        """
        Get the URL for a spreadsheet
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            
        Returns:
            URL to access the spreadsheet
        """
        return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
