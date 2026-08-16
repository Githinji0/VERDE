/* User and BRAIN authentication status manager */

export async function checkSession() {
    return {
        authenticated: true,
        user: "Lead Quant",
        role: "QUANT_RESEARCHER"
    };
}
