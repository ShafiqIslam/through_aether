import { makeStyles } from "@material-ui/core";

const useStyles = makeStyles((theme) => ({
  container: {
    display: "inline-grid",
    gridTemplateColumns: "auto auto auto",
    gap: theme.spacing(1),
    alignItems: "center",
  },
  tokenImg: {
    width: "32px",
  },
  amount: {
    fontWeight: 700,
  },
}));

interface BalanceMessageProps {
  label: string;
  amount: number;
  tokenImgFileName: string;
}

export const BalanceMessage = (props: BalanceMessageProps) => {
  const classes = useStyles();

  return (
    <div className={classes.container}>
      <div>{props.label}</div>
      <div className={classes.amount}>{props.amount}</div>
      <img
        className={classes.tokenImg}
        src={process.env.PUBLIC_URL + "/" + props.tokenImgFileName}
        alt="token logo"
      />
    </div>
  );
};
