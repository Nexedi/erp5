// Type definitions for jio 3.34.0
// Project: https://lab.nexedi.com/nexedi/jio
// Definitions by: Jerome Perrin <https://github.com/perrinjerome>
// Definitions: https://github.com/DefinitelyTyped/DefinitelyTyped (not yet)
// TypeScript Version: 2.4

// XXX needs nexedi RSVP patch loaded.

/**
 * metadata for a document stored in jIO
 */
interface Metadata {
    [key: string]: string;
}

declare class Query {
    /**
     * Serialize a query object to search text
     *
     * @param query a query object
     */
    public static objectToSearchText(query: IQuery): string;
}

interface SimpleQuery extends Query {
    key: string;
    value: any;
    type: "simple";
}

interface ComplexQuery extends Query {
    query_list: Query[];
    operator: "AND" | "OR";
    type: "complex";
}

type IQuery = SimpleQuery | ComplexQuery;

interface AllDocsQuery {
    /**
     * the query
     */
    query: IQuery;

    /**
     * the begin, end limit.
     */
    limit?: [number, number];

    /**
     * list of sort parameters.
     */
    sort_on?: [string, "ascending" | "descending"][];

    /**
     * Which keys from metadata to retrieve
     */
    select_list?: string[];

    /**
     * Shall we retrieve full metadata for all documents ? default false.
     */
    include_docs?: boolean;
}

interface AllDocsResults {
    /**
     * number of returned results
     */
    total_rows: number;
    /**
     * the results
     */
    rows: AllDocsResult[];
}

interface AllDocsResult {
    /**
     * id of the document
     */
    id: string;
    /**
     * metadata associated with the document
     */
    value: Metadata;
}

interface StorageConfiguration {
    /**
     * Storage type
     */
    type: string;
}

interface HandlerStorageConfiguration extends StorageConfiguration {
    /**
     * Sub-storage
     */
    sub_storage: StorageConfiguration;
}

interface MultiHandlerStorageConfiguration extends StorageConfiguration {
    /**
     * Sub-storages
     */
    storage_list?: StorageConfiguration[];
}

interface LocalStorageConfiguration extends StorageConfiguration {
    type: "local";

    /**
     * False (default): create a storage with unlimited duration.
     * True: the storage duration is limited to the user session.
     */
    sessiononly?: boolean;
}

interface MemoryStorageConfiguration extends StorageConfiguration {
    type: "memory";
}

interface IndexedDbStorageConfiguration extends StorageConfiguration {
    type: "indexeddb";
    /**
     * Name of the database
     */
    database: string;
}

interface WebSqlStorageConfiguration extends StorageConfiguration {
    type: "websql";
    /**
     * Name of the database
     */
    database: string;
}

interface WebDavStorageConfiguration extends StorageConfiguration {
    type: "dav";
    /**
     * URL of your WebDAV server.
     */
    url: string;
    /**
     * Login and password of your WebDAV, base64 encoded like this: btoa(username + ":" + password)
     */
    basic_login: string;
    /**
     * False (default): do not send domain cookie.
     * True: send domain cookie.
     */
    with_credentials?: boolean;
}

interface DropboxStorageConfiguration extends StorageConfiguration {
    type: "dropbox";
    /**
     * Access token for your dropbox. See the Dropbox documentation of its API v1 for how to generate an access token.
     */
    access_token: string;
    /**
     * "dropbox" (default) for full access to account files.
     * "sandbox" for only access to files created by your app.
     */
    root: "dropbox" | "sandbox";
}

interface GoogleDriveStorageConfiguration extends StorageConfiguration {
    type: "gdrive";
    /**
     * Access token for your Google Drive. See the Google Drive documentation for how to generate an access token.
     */
    access_token: string;
    /**
     * true (default): sends file to trash bin when calling "remove".
     * false: delete files permanently when calling "remove""
     */
    trashing?: boolean;
}

interface ERP5StorageConfiguration extends StorageConfiguration {
    type: "erp5";
    /**
     * URL of HATEOAS in your ERP5 instance.
     */
    url: string;
    /**
     * Reference of the action used to deliver of the document.
     */
    default_view_reference?: string;
}

interface ZipStorageConfiguration extends HandlerStorageConfiguration {
    type: "zip";
}

interface ShaStorageConfiguration extends HandlerStorageConfiguration {
    type: "sha";
}

interface UuidStorageConfiguration extends HandlerStorageConfiguration {
    type: "uuid";
}
interface QueryStorageConfiguration extends HandlerStorageConfiguration {
    type: "query";
}
interface CryptStorageConfiguration extends HandlerStorageConfiguration {
    type: "crypt";
    /**
     * JSON crypto key.
     */
    key: string;
}

interface UnionStorageConfiguration extends MultiHandlerStorageConfiguration {
    type: "union";
}

interface DocumentStorageConfiguration
    extends MultiHandlerStorageConfiguration {
    type: "document";
    /**
     * id of the document to use.
     */
    document_id: string;
    /**
     * Verify if the document is in good state. (default to false)
     */
    repair_attachment?: boolean;
}

interface ReplicateStorageConfiguration extends StorageConfiguration {
    type: "replicate";
    /**
     * Definition of the local storage, on which normal jIO operations are applied.
     */

    local_sub_storage: StorageConfiguration;
    /**
     * Definition of the remote storage that synchronizes with the local storage.
     */

    remote_sub_storage: StorageConfiguration;
    /**
     * Query object to limit the synchronisation to specific files.
     */

    query: AllDocsQuery;
    /**
     * true: at file modification, modifies the local file id.
     * false (default): at file modification, modifies the remote file id.
     */
    use_remote_post?: boolean;
    /**
     * 0 (default): no conflict resolution (throws error)
     * 1: keep the local state.
     * 2: keep the remote state. 3: keep both states (no signature update)
     */
    conflict_handling?: number;
    /**
     * Control number of parallel operation for document synchronisation. (default 1)
     */
    parallel_operation_amount?: number;
    /**
     * Control number of parallel operation for attachment synchronisation. (default 1)
     */
    parallel_operation_attachment_amount?: number;
    /**
     * Synchronize when local documents are modified. (default true)
     */
    check_local_modification?: boolean;
    /**
     * Synchronize when local documents are created. (default true)
     */
    check_local_creation: boolean;
    /**
     * Synchronize when local documents are deleted. (default true)
     */
    check_local_deletion: boolean;
    /**
     * Synchronize when remote documents are modified. (default true)
     */
    check_remote_modification: boolean;
    /**
     * Synchronize when remote documents are created. (default true)
     */
    check_remote_creation: boolean;
    /**
     * Synchronize when remote documents are deleted. (default true)
     */
    check_remote_deletion: boolean;
    /**
     * Synchronize when local attachments are modified. (default true)
     */
    check_local_attachment_modification: boolean;
    /**
     * Synchronize when local attachments are created. (default false)
     */
    check_local_attachment_creation: boolean;
    /**
     * Synchronize when local attachments are deleted. (default false)
     */
    check_local_attachment_deletion: boolean;
    /**
     * Synchronize when remote attachments are modified. (default false)
     */
    check_remote_attachment_modification: boolean;
    /**
     * Synchronize when remote attachments are created. (default false)
     */
    check_remote_attachment_creation: boolean;
    /**
     * Synchronize when remote attachments are deleted. (default false)
     */
    check_remote_attachment_deletion: boolean;
    /**
     * Use a document key as document signature hash (instead of calculating the SHA1).
     */
    signature_hash_key?: string;
    /**
     * Definition of the signature storage, where replication signature are stored.
     */
    signature_sub_storage: object;
}

declare class jIO {
    /**
     * `createJIO`
     * Initialize a new storage or storage tree, synchronously.
     * @param configuration the configuration to use.
     */
    public static createJIO(
        configuration: LocalStorageConfiguration
    ): LocalStorage;
    public static createJIO(
        configuration: MemoryStorageConfiguration
    ): MemoryStorage;
    public static createJIO(
        configuration: IndexedDbStorageConfiguration
    ): IndexedDbStorage;
    public static createJIO(
        configuration: WebSqlStorageConfiguration
    ): WebSqlStorage;
    public static createJIO(
        configuration: WebDavStorageConfiguration
    ): WebDavStorage;
    public static createJIO(
        configuration: DropboxStorageConfiguration
    ): DropboxStorage;
    public static createJIO(
        configuration: GoogleDriveStorageConfiguration
    ): GoogleDriveStorage;
    public static createJIO(
        configuration: ERP5StorageConfiguration
    ): ERP5Storage;
    public static createJIO(configuration: ZipStorageConfiguration): ZipStorage;
    public static createJIO(configuration: ShaStorageConfiguration): ShaStorage;
    public static createJIO(
        configuration: UuidStorageConfiguration
    ): UuidStorage;
    public static createJIO(
        configuration: QueryStorageConfiguration
    ): QueryStorage;
    public static createJIO(
        configuration: CryptStorageConfiguration
    ): CryptStorage;
    public static createJIO(
        configuration: UnionStorageConfiguration
    ): UnionStorage;
    public static createJIO(
        configuration: ReplicateStorageConfiguration
    ): ReplicateStorage;

    //    function createJIO(configuration: StorageConfiguration): jIOStorage;
}

interface jIOStorage {
    /**
     * `put`: Put Document
     *
     * Create or update the document with the given ID using the given metadata.
     *
     * @param id the document id
     * @param metadata the document metadata
     * @return an promise which resolves when document has been put.
     */
    put(id: string, metadata: Metadata): RSVP.Queue<{}>;

    /**
     * `post`: Post Document
     *
     * Create a new document with the given metadata and returns the automatically generated ID.
     * If post is unsupported, add a UuidStorage handler on top of your storage to provide it.
     *
     * @param metadata the document metadata
     * @returns a promsise which resolves to the new document id once it have been posted.
     */
    post(metadata: Metadata): RSVP.Queue<string>;

    /**
     * `get: Get Document
     *
     *  Retrieve a document's metadata.
     *
     * @param id the document id
     * @returns a promsise which resolves the document metadata.
     */
    get(id: string): RSVP.Queue<Metadata>;

    /**
     * `remove`: Remove Document
     *
     * Deletes a document and all its attachments.
     *
     * @param id the document metadata
     * @returns a promise which resolves once document is removed.
     */
    remove(id: string): RSVP.Queue<{}>;

    /**
     * `allDocs`: Search Documents
     *
     *  Retrieve a list of documents.
     *  If include_docs is true, then doc in the response will contain the full metadata for each document.
     *  Otherwise, if select_list contains keys, then value in the response will contain the values of these keys for each document.
     *  If query is unsupported, add a QueryStorage handler on top of your storage to provide it.
     *
     */
    allDocs(query: AllDocsQuery): RSVP.Queue<AllDocsResults>;

    /**
     * `putAttachment`: Add Attachment
     *
     * Create or update the given blob as an attachment with the given name to the document with the given ID
     *
     * @param id the document id
     * @param name the attachment name
     * @param blob the attachment content
     * @return a promise which will resolve once the attachment is put.
     */
    putAttachment(id: string, name: string, blob: Blob): RSVP.Queue<{}>;

    /**
     * `removeAttachment`: Remove Attachment
     *
     * Deletes the attachment with the given name from the document with the given ID.
     *
     * @param id the document id
     * @param name the attachment name
     * @return a promise which will resolve once the attachment is removed.
     */
    removeAttachment(id: string, name: string, blob: Blob): RSVP.Queue<{}>;

    /**
     * `getAttachment`: Get Attachment
     *
     *  Retrieve the attachment with the given name from the document with the given ID in text, json, blob, data_url, or array_buffer format.
     *
     * @param id the document id
     * @param name the attachment name
     * @return a promise which will resolve with the document.
     */
    getAttachment(
        id: string,
        name: string,
        format: { type: "text" }
    ): RSVP.Queue<string>;
    getAttachment(
        id: string,
        name: string,
        format: { type: "json" }
    ): RSVP.Queue<object>;
    getAttachment(
        id: string,
        name: string,
        format: { type: "blob" }
    ): RSVP.Queue<Blob>;
    getAttachment(
        id: string,
        name: string,
        format: { type: "data_url" }
    ): RSVP.Queue<string>;
    getAttachment(
        id: string,
        name: string,
        format: { type: "array_buffer" }
    ): RSVP.Queue<ArrayBuffer>;

    /**
     * `repair`: Synchronize Storage
     * Synchronize or repair the storage.
     * If repair is unsupported, add a ReplicateStorage handler on top of the two storages you wish to synchronize, to provide it
     * @returns a promise which will resolve when storage is repaired, or be rejected if reparation failed.
     */
    repair(): RSVP.Queue<{}>;
}

/**
 * Store documents in the browser's local storage.
 * This storage has only one document, with the ID "/", so post, put, remove and get methods are not supported.
 * The only operations you can do on a raw LocalStorage are attachment manipulation methods with blobs.
 * To treat a LocalStorage as a regular storage, add a DocumentStorage handler on top of it, with "/" as the document_id.
 */
interface LocalStorage extends jIOStorage {}

/**
 * Store documents in a raw JavaScript object, in memory.
 * The storage's data isn't saved when your web page is closed or reloaded, and doesn't take any other arguments.
 */
interface MemoryStorage extends jIOStorage {}

/**
 * Store documents in the IndexedDB database with the given name.
 */
interface IndexedDbStorage extends jIOStorage {}

/**
 * Store documents in the WebSQL database with the given name. Using an IndexedDBStorage is strictly better.
 */
interface WebSqlStorage extends jIOStorage {}

/**
 * Store documents in the WebDAV server with the given URL.
 * Documents are WebDAV directories, so they must not contain any metadata, and their IDs must be bookended by forward slashes that directly correspond to their path.
 * Attachments to documents are files inside WebDAV directories, so they must not contain any forward slashes.
 * To treat a WebDavStorage as a regular storage, add a FileSystemBridgeStorage on top of it.
 */
interface WebDavStorage extends jIOStorage {}

/**
 * Store documents in the Dropbox account with the given access token.
 * Documents are Dropbox folders, so they must not contain any metadata, and their IDs must be bookended by forward slashes that directly correspond to their path.
 * Attachments to documents are Dropbox files inside Dropbox folders, so they must not contain any forward slashes.
 * To treat a DropboxStorage as a regular storage, add a FileSystemBridgeStorage on top of it.
 */
interface DropboxStorage extends jIOStorage {}

/**
 * Store documents in the Google Drive account with the given access token.
 * Unlike WebDavStorage and DropboxStorage, GoogleDriveStorage documents can contain metadata and have no specific rules regarding forward slashes.
 * To treat a GoogleDriveStorage as a regular storage, add a FileSystemBridgeStorage on top of it.
 */
interface GoogleDriveStorage extends jIOStorage {}

/**
 * Store documents in the ERP5 instance with the given URL.
 * All ERP5 documents must contain values for portal_type and parent_relative_url in the metadata, which define the type of the document that is stored.
 * Attachments are ERP5 actions.
 * A raw Erp5Storage supports post and query, so there is no need to add a UuidStorage or QueryStorage on top of it.
 */
interface ERP5Storage extends jIOStorage {}

/**
 * Compress and decompress attachments to reduce network and storage usage.
 */
interface ZipStorage extends jIOStorage {}

/**
 * Provide the post method to create new documents using the SHA-1 hashes of their parameters as their IDs.
 */
interface ShaStorage extends jIOStorage {}

/**
 * Provide the post method to create new documents using randomly generated UUIDs as their IDs.
 */
interface UuidStorage extends jIOStorage {}

/**
 * Provide support for query parameters in the allDocs method.
 */
interface QueryStorage extends jIOStorage {}

/**
 * Encrypt and decrypt attachments to secure them.
 * You must generate a [Crypto key in JSON format](https://developer.mozilla.org/fr/docs/Web/API/Window/crypto) to use this handler.
 */
interface CryptStorage extends jIOStorage {}

/**
 *This handler takes a list of storages as its argument. When using a jIO method, UnionStorage tries it on the first storage of the array; if it fails, then UnionStorage tries the method on the next storage, and so on until success or there are no more storages left to try.
 */
interface UnionStorage extends jIOStorage {}

/**
 * Create a storage on top of a single document by mapping documents to attachments, so that jIO methods work normally on single-document storages.
 */
interface DocumentStorage extends jIOStorage {}

/**
 * Synchronize documents between a local and a remote storage by providing the repair method.
 */
interface ReplicateStorage extends jIOStorage {}
