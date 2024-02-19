# Sample search application
This project serves as a demo application for the recipes ```Building search experience with Search Application Client ``` and ```Measuring the performance of your search applications with Behaviour analytics```


### Getting Started
1. Install dependencies
```
yarn install
```
2. Update the SearchApplicationClient params in ```App.tsx``` with the ```applicationName```, ```endpoint```, ```apiKey``` and ```params``` for your search experience if needed.
```javascript
const request = SearchApplicationClient(
  /*Application name*/,
  /*Elasticsearch endpoint*/,
  /*API key*/,
  /*Additional params*/
)
```
3. Start server. This will start the server on port 3000.
```
yarn start
```