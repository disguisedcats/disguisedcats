export async function decrypting(encryptedData) {
  const importedKey = await window.crypto.subtle.importKey(
    "jwk",
    JSON.parse(localStorage.getItem('privateKey')),
    {
      name: "RSA-OAEP",
      hash: "SHA-256"
    },
    true,
    ["decrypt"]
  );
  try {
    const decryptedData = await window.crypto.subtle.decrypt({name: 'RSA-OAEP'}, importedKey, encryptedData);
    const decryptedString = new TextDecoder().decode(decryptedData);
    console.log("Decrypted data:", (decryptedString));
    return new Uint8Array(decryptedData);
  } catch (error) {
    console.error("Decryption error:", error);
    return null;
  }
}

export async function crypting(text) {
  try {
    const k = await window.crypto.subtle.generateKey(
      {
        name: "RSA-OAEP",
        modulusLength: 4096,
        publicExponent: new Uint8Array([1, 0, 1]),
        hash: "SHA-256",
      },
      true,
      ["encrypt", "decrypt"],
    );

    const exportedKey = await window.crypto.subtle.exportKey("jwk", k.privateKey);
    const keyString = JSON.stringify(exportedKey);
    localStorage.setItem('privateKey', keyString)

    const uintData = new Uint8Array(text.split('').map(x => x.charCodeAt(0)));

    const encryptedData = await window.crypto.subtle.encrypt({name: 'RSA-OAEP'}, k.publicKey, uintData);
    return encryptedData;
  } catch (error) {
    console.error("Error:", error);
  }
}