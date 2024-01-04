import Routes from "./components/Routes";
import { BrowserRouter } from "react-router-dom";
import { init as initApm } from '@elastic/apm-rum'

export const apm = initApm({
    serviceName: "${ELASTIC_APM_SERVICE_NAME}",
    serverUrl: "${ELASTIC_APM_SERVER_URL}",
    serviceVersion: '',
    environment: "${ELASTIC_APM_ENVIRONMENT}",
    distributedTracingOrigins: ['http://localhost:3000','http://localhost:3001','http://localhost:9000']
})

function App() {
    return (
        <BrowserRouter>
            {/* <Navigation /> */}
            <Routes />
        </BrowserRouter>
    );
}

export default App;
