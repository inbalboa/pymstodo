Getting your own API key
------------------------
You need to get your own Microsoft API key to use `pymstodo`.
1. Sign in to the [Azure portal](https://portal.azure.com/) using a Microsoft account.
2. In the left-hand navigation pane, select the `Azure Active Directory`, then `App registrations > New registration`.
3. When the app registration page appears, click `Register` after entering your application's registration information:
 - Name: any
 - Supported account types: `Accounts in any organizational directory and personal Microsoft accounts`
 - Platform configuration: `Client Application`
4. You will be redirected to the app's authentication page. Under `Platform configurations` click `Add a platform`.
5. Select `Web` and enter `https://localhost/login/authorized` for the `Redirect URI` and click `Configure`.
6. Next, in the left-hand navigation pane, select `Certificates & secrets`.
7. Click `New client secret` and create a secret key. You may use any description. Click `Add`. Make sure to copy the secret key somewhere before leaving the page as you will not be able to view it again.
8. In the left-hand navigation pane, select `Overview`. Copy the `application (client) id` somewhere.

