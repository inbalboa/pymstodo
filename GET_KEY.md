Getting your own API key
------------------------
You have to get your own Microsoft API key to use `pymstodo`.
1. Sign in to the [Azure portal](https://portal.azure.com/) using your Microsoft account.
2. In the left-hand navigation pane, select `All services`, find `App registrations`, then `New registration`.
3. When the app registration page appears, click `Register` after entering your application's registration information:
 - Name: any
 - Supported account types: `Accounts in any organizational directory and personal Microsoft accounts`
 - Redirect URI section: Plarform - `Web`, URI - `https://localhost/login/authorized`
4. You will be redirected to the app's overview page. Save the `Application (client) id` somewhere.
5. Click `Certificates & secrets`, then `New client secret`. Description - any, expires - on your choice. Click `Add`. Make sure to copy the secret key (the `Value` field, not the `Secret ID`!) somewhere before leaving the page as you won't be able to view it again.

