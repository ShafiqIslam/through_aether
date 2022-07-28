import { useEffect, useState } from "react";
import { useEthers, useContractFunction, Notification } from "@usedapp/core";
import { constants, utils } from "ethers";
import TokenFarm from "../chain-info/contracts/TokenFarm.json";
import ERC20 from "../chain-info/contracts/dependencies/OpenZeppelin/openzeppelin-contracts@4.7.0/IERC20.json";
import { Contract } from "@ethersproject/contracts";
import networkMapping from "../chain-info/deployments/map.json";

export const useStakeTokens = (tokenAddress: string) => {
  const { chainId } = useEthers();
  const { abi } = TokenFarm;
  let chainIdStr = chainId ? String(chainId) : "default";
  const chainIdKey = chainIdStr as keyof typeof networkMapping;
  const tokenFarmAddress = chainId ? networkMapping[chainIdKey]["TokenFarm"][0] : constants.AddressZero;
  const tokenFarmInterface = new utils.Interface(abi);
  const tokenFarmContract = new Contract(tokenFarmAddress, tokenFarmInterface);

  const erc20ABI = ERC20.abi;
  const erc20Interface = new utils.Interface(erc20ABI);
  const erc20Contract = new Contract(tokenAddress, erc20Interface);

  const { send: approveErc20Send, state: approveAndStakeErc20State } = useContractFunction(erc20Contract, "approve", {
    transactionName: "Approve ERC20 transfer",
  });

  const approveAndStake = (amount: string) => {
    setAmountToStake(amount);
    return approveErc20Send(tokenFarmAddress, amount);
  };

  const { send: stakeSend, state: stakeState } = useContractFunction(tokenFarmContract, "stake", {
    transactionName: "Stake Tokens",
  });
  const [amountToStake, setAmountToStake] = useState("0");

  useEffect(() => {
    if (approveAndStakeErc20State.status === "Success") {
      stakeSend(tokenAddress, amountToStake);
    }
  }, [approveAndStakeErc20State, amountToStake, tokenAddress]);

  const [state, setState] = useState(approveAndStakeErc20State);

  useEffect(() => {
    if (approveAndStakeErc20State.status === "Success") {
      setState(stakeState);
    } else {
      setState(approveAndStakeErc20State);
    }
  }, [approveAndStakeErc20State, stakeState]);

  return { approveAndStake, state };
};

const isTransactionSuccess = (notification: Notification, name: string) => {
  return notification.type === "transactionSucceed" && notification.transactionName === name;
};

export const isApproved = (notifications: Notification[]) => {
  return (
    notifications.filter((notification) => {
      return isTransactionSuccess(notification, "Approve ERC20 transfer");
    }).length > 0
  );
};

export const isStaked = (notifications: Notification[]) => {
  return (
    notifications.filter((notification) => {
      return isTransactionSuccess(notification, "Stake Tokens");
    }).length > 0
  );
};
