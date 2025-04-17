const jwt = require('jsonwebtoken');
const jwksClient = require('jwks-rsa');

const cognitoDomain = 'us-west-1d6qnsvvw3.auth.us-west-1.amazoncognito.com';
const userPoolId = 'us-west-1_D6qNsVVW3';
const clientId = '19728a63u7oh4r2hjb3u2qeck9';
const region = 'us-west-1';
const redirectUri = 'https://d27us82d2go2e4.cloudfront.net/';

const client = jwksClient({
    jwksUri: `https://cognito-idp.us-west-1.amazonaws.com/us-west-1_D6qNsVVW3/.well-known/jwks.json`
});

function getSigningKey(kid) {
    return new Promise((resolve, reject) => {
        client.getSigningKey(kid, (err, key) => {
            if (err) {
                console.log('Failed to fetch signing key:', err);
                reject(err);
            } else {
                const signingKey = key.publicKey || key.rsaPublicKey;
                console.log('Successfully fetched signing key for kid:', kid);
                resolve(signingKey);
            }
        });
    });
}

async function verifyToken(token) {
    try {
        console.log('Verifying token...');
        const decodedToken = jwt.decode(token, { complete: true });
        if (!decodedToken) {
            console.log('Failed to decode token.');
            return null;
        }

        console.log('Decoded token header:', decodedToken.header);
        const kid = decodedToken.header.kid;
        const signingKey = await getSigningKey(kid);

        const verifiedToken = jwt.verify(token, signingKey, {
            algorithms: ['RS256'],
            issuer: `https://cognito-idp.${region}.amazonaws.com/${userPoolId}`
        });

        console.log('Token successfully verified.');
        return verifiedToken;
    } catch (err) {
        console.log('Token verification failed:', err);
        return null;
    }
}

function extractTokenFromCookies(headers) {
    const cookies = headers.cookie || [];
    console.log('Extracting token from cookies...');
    for (let i = 0; i < cookies.length; i++) {
        const cookieString = cookies[i].value;
        console.log('Found cookie:', cookieString);
        const cookieParts = cookieString.split(';');

        for (const part of cookieParts) {
            const [name, value] = part.trim().split('=');
            if (name === 'id_token') {
                console.log('id_token found.');
                return value;
            }
        }
    }
    console.log('No id_token found in cookies.');
    return null;
}

exports.handler = async (event) => {
    const request = event.Records[0].cf.request;
    const headers = request.headers;
    const uri = request.uri;
    const query = request.querystring;

    console.log('Incoming request:', {
        uri,
        query,
        headers
    });

    if (uri.match(/\.(jpg|jpeg|png|gif|css|js|svg|ico)$/i)) {
        console.log('Skipping auth check for static asset:', uri);
        return request;
    }

    const idToken = extractTokenFromCookies(headers);
    let isAuthenticated = false;

    if (idToken) {
        const decodedToken = await verifyToken(idToken);
        isAuthenticated = !!decodedToken;
        console.log('Authentication status:', isAuthenticated);
    } else {
        console.log('No token to verify.');
    }

    if (!isAuthenticated && !request.querystring.includes('code=')) {
        console.log('Unauthenticated user, redirecting to Cognito login...');
        const loginUrl = `https://${cognitoDomain}/login?client_id=${clientId}&response_type=code&scope=email+openid+profile&redirect_uri=${encodeURIComponent(redirectUri)}`;
        return {
            status: '302',
            statusDescription: 'Found',
            headers: {
                location: [{
                    key: 'Location',
                    value: loginUrl
                }],
                'cache-control': [{
                    key: 'Cache-Control',
                    value: 'no-cache'
                }]
            }
        };
    }

    if (!isAuthenticated && request.querystring.includes('code=')) {
        console.log('User has Cognito code param but is not authenticated yet. Allowing request to proceed...');
        return request;
    }

    console.log('User is authenticated. Allowing request to proceed...');
    return request;
};
