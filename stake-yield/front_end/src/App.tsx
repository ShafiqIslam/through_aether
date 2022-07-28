import { DAppProvider, Config, Localhost } from "@usedapp/core";
import Header from "./components/Header";
import { Container } from "@material-ui/core";
import { Main } from "./components/Main";

const config: Config = {
  networks: [Localhost],
  readOnlyChainId: Localhost.chainId,
  readOnlyUrls: {
    [Localhost.chainId]: "http://localhost:8545",
  },
  notifications: {
    expirationPeriod: 1000,
    checkInterval: 1000,
  },
};

function App() {
  return (
    <DAppProvider config={config}>
      <Header />
      <Container maxWidth="md">
        <Main />
      </Container>
    </DAppProvider>
  );
}

export default App;
