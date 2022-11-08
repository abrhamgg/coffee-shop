/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'dev-dldwpymb7jimc0ra.us', // the auth0 domain prefix
    audience: 'cafe coffee', // the audience set for the auth0 app
    clientId: '6FkmViEGIjqTe2NzFzuw4H72qnQ0YK2j', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:8100', // the base url of the running ionic application. 
  }
};
