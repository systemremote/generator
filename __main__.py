import requests
import asyncio
import aiohttp
import random
import string
import time
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style, init


class TokenGenerator:                                                                                       
      def __init__(self):                                                                                             
          self.base_url = "https://discord.com/api/v9"                                                                
          self.user_agents = [                                                                                        
              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",                                         
              "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"                                    
          ]                                                                                                           
                                                                                                                      
      def generate_user_data(self):                                                                                   
          """Generate fake user data"""                                                                               
          names = ["Alex", "Jordan", "Taylor", "Casey", "Riley", "Avery", "Quinn", "Cameron"]                         
          name = random.choice(names)                                                                                 
          number = random.randint(1000, 9999)                                                                         
          email = f"{name.lower()}.{number}@tempmail.org"                                                             
          password = ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%", k=16))                    
          username = f"{name}{number}"                                                                                
                                                                                                                      
          return {                                                                                                    
              'email': email,                                                                                         
              'password': password,                                                                                   
              'username': username,                                                                                   
              'number': number                                                                                        
          }                                                                                                           
                                                                                                                      
      async def create_token_batch(self, session, batch_size=10):                                                     
          """Create multiple tokens in batch"""                                                                       
          tokens = []                                                                                                 
                                                                                                                      
          for i in range(batch_size):                                                                                 
              user_data = self.generate_user_data()                                                                   
                                                                                                                      
              payload = {                                                                                             
                  'captcha_key': None,                                                                                
                  'consent': True,                                                                                    
                  'email': user_data['email'],                                                                        
                  'gift_code_sku_id': None,                                                                           
                  'fingerprint': await self.get_fingerprint(session),                                                 
                  'password': user_data['password'],                                                                  
                  'username': user_data['username']                                                                   
              }                                                                                                       
                                                                                                                      
              try:
                  async with session.post(f"{self.base_url}/auth/register", headers={
                          'User-Agent': random.choice(self.user_agents),
                          'Content-Type': 'application/json',                                                         
                          'X-Super-Properties':'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzkxLjAuNDQ3Mi4xMjQgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjkxLjAuNDQ3Mi4xMjQiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiJkaXNjb3JkLmNvbSIsInJlZmVycmVyX2N1cnJlbnQiOiJodHRwczovL2Rpc2NvcmQuY29tLyIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6ImRpc2NvcmQuY29tIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6OTM4NTYsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9',                                                   
                          'X-Debug-Options': 'bugReporterEnabled'
                      },                                                                                              
                      json=payload
                  ) as response:                                                                                      
                      if response.status == 201:                                                                      
                          data = await response.json()                                                                
                          token = data.get('token')
                          if token:
                              tokens.append(token)
                              print(f"{Fore.GREEN}[+] Created token: {token[:25]}...")
                      else:
                          error = await response.text()
                          print(f"{Fore.RED}[-] Failed: {error}")

              except Exception as e:
                  print(f"{Fore.RED}[-] Exception: {e}")

          return tokens                                                                                               
                                                                                                                      
      async def get_fingerprint(self, session):                                                                       
          """Get Discord fingerprint"""                                                                               
          try:                                                                                                        
              async with session.get(f"{self.base_url}/experiments") as response:                                     
                  if response.status == 200:                                                                          
                      data = await response.json()                                                                    
                      return data.get('fingerprint', '')                                                              
          except:                                                                                                     
              return ''                                                                                               
                                                                                                                      
      async def generate_tokens(self, total_tokens=100, batch_size=10, concurrent_batches=3):                         
          """Generate large number of tokens"""                                                                       
          print(f"{Fore.CYAN}[INFO] Generating {total_tokens} tokens...")                                             

          all_tokens = []
                                                                                                                      
          async with aiohttp.ClientSession() as session:
              batches_needed = (total_tokens + batch_size - 1) // batch_size

              for batch_num in range(batches_needed):
                  print(f"{Fore.CYAN}[INFO] Processing batch {batch_num + 1}/{batches_needed}")


                  tasks = []                                                                                          
                  for _ in range(concurrent_batches):                                                                 
                      if len(all_tokens) >= total_tokens:                                                             
                          break                                                                                       
                      tasks.append(self.create_token_batch(session, batch_size))                                      
                                                                                                                      
                  batch_results = await asyncio.gather(*tasks)                                                        
                                                                                                                      

                  for batch_tokens in batch_results:                                                                  
                      all_tokens.extend(batch_tokens)
                      if len(all_tokens) >= total_tokens:                                                             
                          break                                                                                       
                                                                                                                      

                  with open('generated_tokens.txt', 'a') as f:                                                        
                      for token in batch_tokens:                                                                      
                          f.write(f"{token}\n")                                                                       
                                                                                                                      
                  print(f"{Fore.CYAN}[INFO] Progress: {len(all_tokens)}/{total_tokens} tokens")                       
                                                                                                                      
                  await asyncio.sleep(2)                                                                              
                                                                                                                      
          print(f"{Fore.GREEN}[SUCCESS] Generated {len(all_tokens)} tokens!")                                         
          return all_tokens                                                                                           
                                                                                                                      
async def main():                                                                                                   
      generator = TokenGenerator()                                                                            
                                                                                                                      
      total = int(input("How many tokens to generate? "))                                                             
      batch_size = int(input("Batch size? "))                                                                         
      concurrent = int(input("Concurrent batches? "))                                                                 
                                                                                                                      
      tokens = await generator.generate_tokens(total, batch_size, concurrent)                                         
                                                                                                                      
      print(f"{Fore.CYAN}[INFO] Tokens saved to generated_tokens.txt")
                                                                                                                      
if __name__ == "__main__":                                                                                          
      asyncio.run(main())                                                                                             
