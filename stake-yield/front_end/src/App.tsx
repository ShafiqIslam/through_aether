import React from "react";
import { DAppProvider, ChainId, Config } from "@usedapp/core";
import Header from "./components/Header";

const config: Config = {
  supportedChains: [ChainId.Rinkeby, 1337],
};

function App() {
  return (
    <DAppProvider config={config}>
      <Header></Header>
    </DAppProvider>
  );
}

export default App;
