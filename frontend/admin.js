const ADMIN_KEY = prompt("Enter admin key");

function addOutput(text) {

    const table = document.getElementById("docs-body");

    const row = document.createElement("tr");

    row.innerHTML = `
        <td colspan="4" style="padding:10px;color:#666;">${text}</td>
    `;

    table.appendChild(row);
}


async function uploadPDF() {

    const file = document.getElementById("pdf-file").files[0];

    if (!file) {
        alert("Select a PDF first");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("/admin/upload-pdf", {
        method: "POST",
        headers: {
            "X-Admin-Key": ADMIN_KEY
        },
        body: formData
    });

    const data = await res.json();

    alert(data.message);

    loadDocuments();
}



async function loadDocuments() {

    const res = await fetch("/admin/documents", {
        headers: {
            "X-Admin-Key": ADMIN_KEY
        }
    });

    const data = await res.json();

    const body = document.getElementById("docs-body");

    body.innerHTML = "";

    for (const doc in data) {

        const row = document.createElement("tr");

        row.innerHTML = `
            <td style="padding:10px;">${doc}</td>
            <td style="padding:10px;">${data[doc].category}</td>
            <td style="padding:10px;">${data[doc].chunks}</td>
            <td style="padding:10px;">
                <button onclick="deleteDoc('${doc}')">Delete</button>
            </td>
        `;

        body.appendChild(row);
    }

}



async function deleteDoc(source) {

    if (!confirm("Delete this document?")) return;

    const res = await fetch("/admin/delete", {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json",
            "X-Admin-Key": ADMIN_KEY
        },
        body: JSON.stringify({
            source: source
        })
    });

    const data = await res.json();

    alert(data.message);

    loadDocuments();

}



async function showStats() {

    const res = await fetch("/admin/stats", {
        headers: {
            "X-Admin-Key": ADMIN_KEY
        }
    });

    const data = await res.json();

    alert(
        "Documents: " + data.documents +
        "\nChunks: " + data.chunks
    );

}



async function deleteAll() {

    if (!confirm("Delete ALL documents?")) return;

    const res = await fetch("/admin/delete-all", {
        method: "DELETE",
        headers: {
            "X-Admin-Key": ADMIN_KEY
        }
    });

    const data = await res.json();

    alert(data.message);

    loadDocuments();

}



// Load documents automatically
loadDocuments();