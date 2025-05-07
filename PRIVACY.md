# Rookie Data Alchemy Plugin Privacy Policy

## 1. Information Collection Statement  
​**​This plugin does NOT collect or require:​**​  
- Personal user information (name, email, device identifiers, etc.)  
- User behavior data (usage patterns,  durations, etc.)  
- Device information (IP addresses, OS versions, etc.)  

​**​Data Processing Disclosure:​**​  
- Processes user-provided JSON data exclusively for chart generation  
- Transmits JSON data and chart-type specifications to authorized AI model APIs  
- Does not attach any user metadata to API requests  

---

## 2. Data Handling Scope  
​**​Core Functionality:​**​  
1. Receives structured JSON input and chart configuration parameters  
2. Transforms data through AI model APIs into ECharts-compatible specifications  
3. Returns visualization code without retaining source data  

​**​Processing Guarantees:​**​  
- No persistent storage of user JSON data (volatile memory only)  
- No analysis of JSON content for non-visualization purposes  
- No linkage between chart requests and user identities  

---

## 3. Third-Party Integrations  
​**​AI Model Provider:​**​  
- Utilizes [Insert AI Model Provider Name] API ([link to provider's TOS](https://example.com))  
- JSON data subject to provider's privacy policy ([link to provider's policy](https://example.com))  

​**​ECharts Dependency:​**​  
- Implements Apache ECharts ([official site](https://echarts.apache.org)) under Apache 2.0 License  
- Chart rendering occurs client-side without external data transmission  

---

## 4. Security Protocols  
​**​End-to-End Protection:​**​  
- Enforces HTTPS (TLS 1.3+) for all API communications  
- Implements request payload encryption compatible with AI provider standards  

​**​Ephemeral Processing:​**​  
- Automatically purges JSON input from memory upon:  
  - Successful chart generation  
  - Plugin session termination  
  - 15 minutes of inactivity (whichever comes first)  

---

## 5. User Responsibilities  
- Ensure JSON data contains no sensitive/regulated information  
- Maintain independent backups of source data  
- Verify AI model provider's compliance with regional data regulations  

---

## 6. Policy Updates  
This policy may be revised with plugin updates. Continued usage constitutes acceptance of amendments. Current version effective: [Insert Date]  

​**​Contact:​**​ 18829526908@163.com

