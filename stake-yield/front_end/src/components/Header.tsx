import { useEthers } from "@usedapp/core";
import { Button, makeStyles } from "@material-ui/core";

const useStyles = makeStyles((theme) => ({
  container: {
    padding: theme.spacing(4),
    display: "flex",
    justifyContent: "flex-end",
    gap: theme.spacing(1),
  },
}));

function Header() {
  const { account, activateBrowserWallet, deactivate } = useEthers();
  const isConnected = account != undefined;

  let classes = useStyles();

  return (
    <div className={classes.container}>
      <div>
        {isConnected ? (
          <Button color="primary" variant="contained" onClick={deactivate}>
            Disconnect
          </Button>
        ) : (
          <Button
            color="primary"
            variant="contained"
            onClick={activateBrowserWallet}
          >
            Connect
          </Button>
        )}
      </div>
    </div>
  );
}

export default Header;
