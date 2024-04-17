# Unveiling Trends: Exploring Baby Names in the United States
A Capstone Project for the Master of Applied Data Science Degree (University of Michigan School of Information) by Team 12 The Name Droppers (Jonathan Ellis, Jordan Marquez and Paul Schickler)

![Wordcloud of Top Names from Last Decade](Wordcloud.png)

## Overview
Our project analyzes long-term US naming trends using the Social Security Administration's (SSA) baby name dataset from 1881 to 2022. We examine sex, counts, and state-level variations to identify historical naming shifts and regional differences. Additionally, we identify pop culture naming trends and build a forecasting model for names.

## Dataset
This project uses baby name data from the Social Security Adminstration (SSA).  

The data can be downloaded from: https://www.ssa.gov/oact/babynames/limits.html
    National data: there is a txt file for each year of birth (1881-2022). Columns: name, M/F, and count. 
    State-specific data: there is a txt file for each state (and DC). Columns: state, M/F, year, name, count.

The national data contains 102,449 unique names. The state data contains 32,722 unique names and the state data has ~12% fewer counts than the national data. For privavy reasons, the SSA excluded names with fewer than 5 occurences in any geographic area. 
