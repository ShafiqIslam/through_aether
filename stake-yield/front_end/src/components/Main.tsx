import { useEthers } from "@usedapp/core";
import helperConfig from "../helper-config.json";
import { makeStyles } from "@material-ui/core";
import { constants } from "ethers";
import networkMapping from "../chain-info/deployments/map.json";
import brownieConfig from "../brownie-config.json";
import { YourWallet } from "./your-wallet";

const useStyles = makeStyles((theme) => ({
  title: {
    color: theme.palette.common.white,
    textAlign: "center",
    padding: theme.spacing(4),
  },
}));

export type Token = {
  image: string;
  address: string;
  name: string;
};

export const Main = () => {
  const classes = useStyles();
  const { account, chainId } = useEthers();
  let chainIdStr = chainId ? String(chainId) : "default";
  const chainIdKey = chainIdStr as keyof typeof networkMapping;
  const dappAddress = chainId ? networkMapping[chainIdKey]["DappToken"][0] : constants.AddressZero;
  const wethAddress = chainId ? networkMapping[chainIdKey]["MockWETH"][0] : constants.AddressZero;
  const fauAddress = chainId ? networkMapping[chainIdKey]["MockFAU"][0] : constants.AddressZero;

  const supportedTokens: Array<Token> = [
    {
      image: "dapp.png",
      address: dappAddress,
      name: "DAPP",
    },
    {
      image: "eth.png",
      address: wethAddress,
      name: "WETH",
    },
    {
      image: "dai.png",
      address: fauAddress,
      name: "DAI",
    },
  ];

  return (
    <>
      <h2 className={classes.title}>Dapp Token App</h2>
      <YourWallet supportedTokens={supportedTokens} />
    </>
  );
};
