## rookie_data_alchemy

**Author:** jaguarliuu
**Version:** 0.0.1
**Type:** tool

### Description

Transform JSON data into interactive charts effortlessly using AI. Supports all major ECharts visualization types with customizable styling.


### Basic Usage

1. ​**​Install from Marketplace​**​  
   Visit your platform's plugin marketplace and search for "rookie_data_alchemy".  
   Click ​**​Install​**​ to add the plugin to your dify.

2. Launch the plugin after installation.

3. Provide the following parameters:
   - ​**​Data (JSON):​**​  
     Your structured dataset in valid JSON format  
     *Example:*  
     ```json
     {
       "categories": ["Mon", "Tue", "Wed", "Thu", "Fri"],
       "values": [120, 200, 150, 80, 70]
     }
     ```
   - ​**​Chart Type:​**​  
     Enter the ​**​Chinese name​**​ of your desired visualization (e.g. 柱状图, 折线图, 饼图)
   - ​**​Custom Prompts (Optional):​**​  
     Specify styling preferences:  
     `"Use blue theme with data labels"`  
     `"Show horizontal bar chart with gradient fills"`

4. Click ​**​Start Execution​**​ to generate your chart

## 📌 Parameter Details

### 1. Data Requirements
- Strictly formatted JSON
- Supports nested structures for complex charts
- Maximum file size: 5MB

### 2. Supported Chart Types
| Chinese Name | English Equivalent       |
|--------------|--------------------------|
| 柱状图        | Bar Chart                |
| 折线图        | Line Chart               |
| 饼图          | Pie Chart                |
| 散点图        | Scatter Plot             |
| 雷达图        | Radar Chart              |
| 漏斗图        | Funnel Chart             |
| *[Full list in documentation]* | |

### 3. Custom Prompts
Use natural language to request:
- Color schemes
- Component modifications
- Layout adjustments
- Animation preferences

---

## 🎯 Example Use Case

​**​Input Parameters:​**​
```json
Data:
{
  "sales": {
    "Q1": 45000,
    "Q2": 52000,
    "Q3": 48000,
    "Q4": 61000
  }
}

Chart Type: 饼图

Custom Prompt: "Show percentage values with goldenrod colors"
```

**​Output:​​**
Interactive pie chart with annotated percentages in goldenrod palette.