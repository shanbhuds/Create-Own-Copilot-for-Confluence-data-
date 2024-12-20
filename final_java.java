import com.azure.storage.blob.*;
import com.azure.storage.blob.models.*;
import java.io.*;
import java.net.*;
import java.nio.file.*;
import java.util.*;
import javax.net.ssl.HttpsURLConnection;

public class ConfluenceToAzureBlob {

    private static final String CONFLUENCE_BASE_URL = "https://atlassian-dc-test.miniorange.com/wiki";
    private static final String PARENT_PAGE_ID = "2506391559";
    private static final String AUTH_USER = "mo_conf_admin";
    private static final String AUTH_PASS = "L#1wmHQE";
    private static final String AZURE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=csg100320005363b3a0;AccountKey=9n7oVbv+T6PA0lcW9cjwCutlTOxD1W2pWvhS4qCSj/swGMWdVZIG/CrN/IqcHl1UcEvdzA56NIUd+AStmoV1OQ==;EndpointSuffix=core.windows.net";
    private static final String CONTAINER_NAME = "confluencedemo";

    public static void main(String[] args) {
        try {
            BlobServiceClient blobServiceClient = new BlobServiceClientBuilder().connectionString(AZURE_CONNECTION_STRING).buildClient();
            BlobContainerClient containerClient = blobServiceClient.getBlobContainerClient(CONTAINER_NAME);

            if (!containerClient.exists()) {
                containerClient.create();
                System.out.println("Container '" + CONTAINER_NAME + "' created successfully.");
            } else {
                System.out.println("Container already exists, we can append data in the same.");
            }

            processPage(PARENT_PAGE_ID, "", containerClient);
        } catch (Exception e) {
            System.out.println("Failed to connect to Azure Blob Storage: " + e.getMessage());
        }
    }

    private static void processPage(String pageId, String path, BlobContainerClient containerClient) {
        try {
            // Get page content
            Map<String, String> pageContent = getPageContent(pageId);
            String title = pageContent.get("title");
            String content = pageContent.get("content");
            String createdDate = pageContent.get("createdDate");

            // Define blob name based on path and title
            String blobName = Paths.get(path, title + ".html").toString().replace("\\", "/");
            Map<String, String> metadata = new HashMap<>();
            metadata.put("created_date", createdDate);

            // Upload content to Azure Blob Storage
            uploadToAzureBlob(content, blobName, metadata, containerClient);

            // Get child pages and process them recursively
            List<String> childPages = getChildPages(pageId);
            for (String childId : childPages) {
                processPage(childId, Paths.get(path, title).toString(), containerClient);
            }
        } catch (IOException e) {
            System.out.println("An error occurred: " + e.getMessage());
        }
    }

    private static Map<String, String> getPageContent(String pageId) throws IOException {
        String url = CONFLUENCE_BASE_URL + "/rest/api/content/" + pageId;
        URL obj = new URL(url);
        HttpsURLConnection con = (HttpsURLConnection) obj.openConnection();
        con.setRequestMethod("GET");
        String auth = AUTH_USER + ":" + AUTH_PASS;
        String encodedAuth = Base64.getEncoder().encodeToString(auth.getBytes());
        con.setRequestProperty("Authorization", "Basic " + encodedAuth);
        con.setRequestProperty("Content-Type", "application/json");

        int responseCode = con.getResponseCode();
        if (responseCode == HttpsURLConnection.HTTP_OK) {
            BufferedReader in = new BufferedReader(new InputStreamReader(con.getInputStream()));
            String inputLine;
            StringBuilder response = new StringBuilder();
            while ((inputLine = in.readLine()) != null) {
                response.append(inputLine);
            }
            in.close();

            // Parse JSON response
            Map<String, String> result = new HashMap<>();
            // Assuming a JSON parsing library is used here to extract title, content, and createdDate
            // result.put("title", ...);
            // result.put("content", ...);
            // result.put("createdDate", ...);
            return result;
        } else {
            throw new IOException("Failed to get page content. HTTP response code: " + responseCode);
        }
    }

    private static List<String> getChildPages(String parentPageId) throws IOException {
        String url = CONFLUENCE_BASE_URL + "/rest/api/content/" + parentPageId + "/child/page";
        URL obj = new URL(url);
        HttpsURLConnection con = (HttpsURLConnection) obj.openConnection();
        con.setRequestMethod("GET");
        String auth = AUTH_USER + ":" + AUTH_PASS;
        String encodedAuth = Base64.getEncoder().encodeToString(auth.getBytes());
        con.setRequestProperty("Authorization", "Basic " + encodedAuth);
        con.setRequestProperty("Content-Type", "application/json");

        int responseCode = con.getResponseCode();
        if (responseCode == HttpsURLConnection.HTTP_OK) {
            BufferedReader in = new BufferedReader(new InputStreamReader(con.getInputStream()));
            String inputLine;
            StringBuilder response = new StringBuilder();
            while ((inputLine = in.readLine()) != null) {
                response.append(inputLine);
            }
            in.close();

            // Parse JSON response
            List<String> childPages = new ArrayList<>();
            // Assuming a JSON parsing library is used here to extract child page IDs
            // childPages.add(...);
            return childPages;
        } else {
            throw new IOException("Failed to get child pages. HTTP response code: " + responseCode);
        }
    }

    private static void uploadToAzureBlob(String content, String blobName, Map<String, String> metadata, BlobContainerClient containerClient) {
        try {
            BlobClient blobClient = containerClient.getBlobClient(blobName);
            if (blobClient.exists()) {
                ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
                blobClient.download(outputStream);
                String existingContent = outputStream.toString("UTF-8");
                content = existingContent + content;
            }
            blobClient.upload(new ByteArrayInputStream(content.getBytes()), content.length(), true);
            blobClient.setMetadata(metadata);
            System.out.println("Uploaded " + blobName + " to Azure Blob Storage.");
        } catch (Exception e) {
            System.out.println("Failed to upload " + blobName + ": " + e.getMessage());
        }
    }
}
