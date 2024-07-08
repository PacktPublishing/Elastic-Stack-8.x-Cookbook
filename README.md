# Elastic Stack 8.x Cookbook

<a href="https://www.packtpub.com/en-in/product/elastic-stack-8x-cookbook-9781837634293?type=print"><img src="https://content.packt.com/_/image/original/B19799/cover_image_large.jpg" alt="no-image" height="256px" align="right"></a>

This is the code repository for [Elastic Stack 8.x Cookbook](https://www.packtpub.com/en-in/product/elastic-stack-8x-cookbook-9781837634293?type=print), published by Packt.

**Over 80 recipes to perform ingestion, search, visualization, and monitoring for actionable insights**

## What is this book about?
With its practical approach and real-world examples, this essential resource explores the full potential of Elastic Stack for data-driven projects. Learn how to build scalable and efficient data analytics and search solutions using Elastic Stack.

This book covers the following exciting features:
* Discover techniques for collecting data from diverse sources
* Visualize data and create dashboards using Kibana to extract business insights
* Explore machine learning, vector search, and AI capabilities of Elastic Stack
* Handle data transformation and data formatting
* Build search solutions from the ingested data
* Leverage data science tools for in-depth data exploration
* Monitor and manage your system with Elastic Stack

If you feel this book is for you, get your [copy](https://www.amazon.com/Elastic-Stack-8-x-Cookbook-visualization/dp/1837634297/ref=sr_1_1?crid=2S0V1UFAL5NGZ&dib=eyJ2IjoiMSJ9.CTEs7jsRYaMIu-EJ5gI8dp5iR09tvh4lCTfVDPFqWdj0hAAMJ26EdkiU6tnLayem-b4n2Egi5gQ1BNLdCEdNKMnaRlNRfAVI5G7azyWi8lY.h447jMAQ1Eh2-Ok3aF5v44PDWKxJcn0S8AgoNO3GdHg&dib_tag=se&keywords=elastic+stack+8.x+cookbook&qid=1720415263&sprefix=Elastic+stack+%2Caps%2C388&sr=8-1) today!
<a href="https://www.packtpub.com/?utm_source=github&utm_medium=banner&utm_campaign=GitHubBanner"><img src="https://raw.githubusercontent.com/PacktPublishing/GitHub/master/GitHub.png" 
alt="https://www.packtpub.com/" border="5" /></a>
## Instructions and Navigations
This repository contains working versions of the snippets provided in the book to help you to make the most of the Elastic Stack (ELK Stack). All of the code is organized into folders. For example, Chapter3.

The code will look like the following:
```
GET /movies/_search
{
  "query": {
    "multi_match": {
      "query": "come home",
      "fields": ["title", "plot"]
    }
  }
}
```

## Quick links to the chapters
1. [Getting Started – Installing
  the Elastic Stack](Chapter1)
2. [Ingesting General Content Data](Chapter2)
3. [Building Search Applications](Chapter3)
4. [Timestamped Data Ingestion](Chapter4)
5. [Transform Data](Chapter5)
6. [Visualize and Explore Data](Chapter6)
7. [Alerting and
   Anomaly Detection](Chapter7)
8. [Advanced Data
   Analysisand Processing](Chapter8)
9. [Vector Search and Generative AI Integration](Chapter9)
10. [Elastic Observability Solution](Chapter10)
11. [Managing Access Control](Chapter11)
12. [Elastic Stack Operation](Chapter12)
13. [Elastic Stack Monitoring](Chapter13)


**Following is what you need for this book:**
This book is for Elastic Stack users, developers, observability practitioners, and data professionals ranging from beginner to expert level. If you’re a developer, you’ll benefit from the easy-to-follow recipes for using APIs and features to build powerful applications, and if you’re an observability practitioner, this book will help you with use cases covering APM, Kubernetes, and cloud monitoring. For data engineers and AI enthusiasts, the book covers dedicated recipes on vector search and machine learning. No prior knowledge of the Elastic Stack is required.

With the following software and hardware list you can run all code files present in the book (Chapter 1-13).
## Software and Hardware List
 Software required | OS required |
| ------------------------------------ | ----------------------------------- |
| Elastic Stack 8.12 | Windows, macOS, or Linux |
| Python 3.11+ |  |
| Docker 4.27.0 | |
| Kubernetes 1.24+ |  |
| Node.js 19+ |  |
| Terraform 1.8.0 |  |
| Amazon Web Services (AWS) |  |
| Google Cloud Platform (GCP) | |
| Okta |  |
| Ollama |  |
| OpenAI/Azure OpenAI |  |

## Related products
* Vector Search for Practitioners with Elastic [[Packt]](https://www.packtpub.com/en-in/product/vector-search-for-practitioners-with-elastic-9781805121022?type=print) [[Amazon]](https://www.amazon.com/Vector-Search-Practitioners-Elastic-observability/dp/1805121022/ref=sr_1_1?crid=3RY8YNF38X9KG&dib=eyJ2IjoiMSJ9.r8q88QE9fkss7e7-tsb9dw.vPChMCrBClSvQc2mx61Pq0NdULcbga9K4Rvvs3CECPo&dib_tag=se&keywords=Vector+Search+for+Practitioners+with+Elastic&qid=1720416090&sprefix=vector+search+for+practitioners+with+elastic%2Caps%2C660&sr=8-1)

* Getting Started with DuckDB [[Packt]](https://www.packtpub.com/en-in/product/getting-started-with-duckdb-9781803241005?type=print) [[Amazon]](https://www.amazon.com/Getting-Started-DuckDB-practical-efficiently/dp/1803241004/ref=sr_1_1?crid=1812VJAVXIBJ5&dib=eyJ2IjoiMSJ9.miwSyh5Ydw3YOxl8R0qRXg.0MYjqb4kUPh-t3Xa6COS1esLTuP5Ffju5MGilppuxOc&dib_tag=se&keywords=simon+aubury&qid=1720416305&sprefix=simon+aubury%2Caps%2C364&sr=8-1)

## Get to Know the Authors
**Huage Chen**
 is a member of Elastic's Solutions Architecture team for over 4 years, helping users across Europe create cloud-based solutions for search, data analysis, observability, and security. Prior to joining Elastic, he worked for 10 years in the field of web content management, web portals, and digital experience platforms. Huage holds a master&rsquo;s degree in computer science from INSA de Lyon.

**Yazid Akadiri**
 is a solution architect at Elastic for over 4 years, helping organizations and users solve their data and most critical business issues by harnessing the power of the Elastic Stack. At Elastic, he works with a broad range of customers with a particular focus on Elastic observability and security solutions. He previously worked in web services oriented architecture focusing on API management and helping organizations build modern applications.

For any feedback or suggestions, please reach out to the authors at huage.chen_at_elastic.co and yazid.akadiri_at_elastic.co

