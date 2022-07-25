import { DAppProvider, Config, Localhost, ChainId } from "@usedapp/core";
import Header from "./components/Header";
import { Container } from "@material-ui/core";
import { Main } from "./components/Main";

const config: Config = {
  networks: [Localhost],
  readOnlyChainId: ChainId.Localhost,
  readOnlyUrls: {
    [ChainId.Localhost]: "http://localhost:8545",
  },
  multicallAddresses: {
    [ChainId.Localhost]: "0x0FB54156B496b5a040b51A71817aED9e2927912E",
  },
};

function App() {
  return (
    <DAppProvider config={config}>
      <Header></Header>
      <Container maxWidth="md">
        <Main />
      </Container>
    </DAppProvider>
  );
}

export default App;
