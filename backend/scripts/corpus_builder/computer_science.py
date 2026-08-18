"""Computer Science Domain Knowledge Generator.
Comprehensive coverage of Programming, Data Structures, Algorithms, OOP, Databases, OS, Networking, Web Dev.
"""
from __future__ import annotations

def get_computer_science_documents() -> list[dict]:
    docs = []
    
    # 1. Programming Languages
    lang_data = [
        ("tech-lang-python", "Python Programming Language", "programming",
         "Python is a high-level, interpreted, dynamically-typed programming language created by Guido van Rossum. It emphasizes code readability with significant whitespace indentation. Python features a comprehensive standard library and extensive third-party package ecosystem (PyPI) widely used in data science, artificial intelligence, web development, and automation."),
        ("tech-lang-c", "The C Programming Language", "programming",
         "C is a foundational procedural, statically-typed compiled language developed by Dennis Ritchie at Bell Labs. C provides low-level memory access via pointers, direct mapping to hardware machine instructions, and minimal runtime overhead, making it standard for operating systems, device drivers, and embedded systems."),
        ("tech-lang-cpp", "C++ Programming Language", "programming",
         "C++ is a general-purpose compiled programming language designed by Bjarne Stroustrup as an extension of C. It supports object-oriented, generic, and functional programming paradigms with zero-cost abstractions, RAII (Resource Acquisition Is Initialization), smart pointers, and the Standard Template Library (STL)."),
        ("tech-lang-java", "Java Programming Language", "programming",
         "Java is a class-based, object-oriented programming language designed by James Gosling at Sun Microsystems. Java follows the 'Write Once, Run Anywhere' (WORA) philosophy by compiling source code into bytecode executed on the Java Virtual Machine (JVM) with automated garbage collection."),
        ("tech-lang-javascript", "JavaScript Programming Language", "programming",
         "JavaScript is a high-level, interpreted or JIT-compiled programming language that conforms to the ECMAScript specification. As the core scripting language of the World Wide Web alongside HTML and CSS, JavaScript features first-class functions, prototype-based inheritance, dynamic typing, and event-driven asynchronous execution via the event loop."),
        ("tech-lang-typescript", "TypeScript Programming Language", "programming",
         "TypeScript is an open-source, strongly-typed superset of JavaScript developed by Microsoft. It adds static type definitions, compile-time type checking, interfaces, and generics to JavaScript, compiling down to standard JavaScript runnable in any browser or Node.js environment."),
        ("tech-lang-rust", "Rust Programming Language", "programming",
         "Rust is a modern systems programming language focused on memory safety, concurrency, and performance. Rust achieves memory safety without a garbage collector through its compile-time ownership, borrowing, and lifetime system, preventing data races, null pointer dereferences, and buffer overflows."),
        ("tech-lang-go", "Go Programming Language (Golang)", "programming",
         "Go (Golang) is an open-source, statically-typed compiled language created at Google by Robert Griesemer, Rob Pike, and Ken Thompson. Go emphasizes simplicity, fast compilation, memory safety, and native concurrency through goroutines and channels."),
    ]
    for doc_id, title, topic, text in lang_data:
        docs.append({
            "document_id": doc_id,
            "passage_id": f"{doc_id}-1",
            "title": title,
            "domain": "computer_science",
            "topic": topic,
            "language": "en",
            "source_type": "curated",
            "keywords": [k.lower() for k in title.split()],
            "text": text
        })

    # 2. Data Structures
    ds_data = [
        ("tech-ds-array", "Arrays Data Structure", "data_structures",
         "An array is a linear data structure that stores elements of identical data types in contiguous memory locations. Elements are accessed in O(1) constant time using zero-based numerical indices. Fixed-size arrays require pre-allocated memory, while dynamic arrays (such as Python lists or C++ std::vector) resize dynamically with amortized O(1) append operations."),
        ("tech-ds-linked-list", "Linked Lists", "data_structures",
         "A linked list is a linear collection of data elements called nodes, where each node stores a data value and a pointer (or reference) to the next node in sequence. Doubly linked lists maintain pointers to both next and previous nodes. Linked lists allow O(1) insertion and deletion at known positions without memory shifting, but require O(n) sequential access."),
        ("tech-ds-stack", "Stack Data Structure", "data_structures",
         "A stack is an abstract linear data structure adhering to the Last-In, First-Out (LIFO) principle. Core operations include push (insert element at the top) and pop (remove and return the top element), both operating in O(1) time complexity. Stacks are fundamental in function call management, expression parsing, undo/redo buffers, and backtracking algorithms."),
        ("tech-ds-queue", "Queue Data Structure", "data_structures",
         "A queue is a linear data structure that adheres to the First-In, First-Out (FIFO) principle. Elements are inserted at the rear (enqueue) and removed from the front (dequeue), each with O(1) time complexity. Variations include circular queues, double-ended queues (deques), and priority queues."),
        ("tech-ds-hash-table", "Hash Tables and Hash Maps", "data_structures",
         "A hash table (or hash map) is an associative data structure that stores key-value pairs. It uses a hash function to compute an integer index into an array of buckets where the desired value can be found. On average, search, insertion, and deletion operate in O(1) time. Hash collisions are resolved using separate chaining or open addressing (linear probing)."),
        ("tech-ds-binary-tree", "Binary Trees and Binary Search Trees (BST)", "data_structures",
         "A binary tree is a hierarchical non-linear data structure where each node has at most two children, referred to as the left and right child. A Binary Search Tree (BST) maintains the ordering invariant: every node in the left subtree has a key strictly less than the node's key, and every node in the right subtree has a key strictly greater. Average lookup, insertion, and deletion take O(log n) time."),
        ("tech-ds-balanced-bst", "Self-Balancing Trees (AVL and Red-Black Trees)", "data_structures",
         "Self-balancing binary search trees, such as AVL trees and Red-Black trees, automatically maintain logarithmic tree height during insertions and deletions. By performing tree rotations upon height violations, they guarantee worst-case O(log n) time complexity for search, insert, and delete operations."),
        ("tech-ds-heap", "Heaps and Priority Queues", "data_structures",
         "A heap is a specialized tree-based data structure satisfying the heap property: in a max-heap, the parent node is always greater than or equal to its children; in a min-heap, the parent is less than or equal to its children. Implemented as complete binary trees backed by flat arrays, heaps support O(1) peek and O(log n) insertion and extraction, widely used in Dijkstra's algorithm and heapsort."),
        ("tech-ds-graph", "Graph Data Structures", "data_structures",
         "A graph is a non-linear data structure consisting of a finite set of vertices (or nodes) connected by edges. Graphs can be directed or undirected, weighted or unweighted, cyclic or acyclic. Graphs are commonly represented using adjacency matrices (O(V^2) space, O(1) edge lookup) or adjacency lists (O(V + E) space, optimal for sparse graphs)."),
        ("tech-ds-trie", "Tries and Prefix Trees", "data_structures",
         "A trie (prefix tree) is a tree-like search data structure used to store associative arrays where keys are strings. Each node represents a common prefix of strings, allowing string search, prefix matching, and autocomplete operations in O(k) time, where k is the string length, independent of total stored items.")
    ]
    for doc_id, title, topic, text in ds_data:
        docs.append({
            "document_id": doc_id,
            "passage_id": f"{doc_id}-1",
            "title": title,
            "domain": "computer_science",
            "topic": topic,
            "language": "en",
            "source_type": "curated",
            "keywords": [k.lower() for k in title.split()],
            "text": text
        })

    # 3. Algorithms
    algo_data = [
        ("tech-algo-big-o", "Algorithmic Complexity and Big-O Notation", "algorithms",
         "Big-O notation describes the limiting behavior of an algorithm's execution time or memory space as input size n approaches infinity. Common time complexity classes include O(1) constant, O(log n) logarithmic, O(n) linear, O(n log n) linearithmic, O(n^2) quadratic, and O(2^n) exponential."),
        ("tech-algo-sorting", "Sorting Algorithms (Quicksort, Mergesort, Heapsort)", "algorithms",
         "Sorting algorithms arrange elements in a specified order. Quicksort uses a divide-and-conquer strategy with a pivot, achieving average O(n log n) time. Mergesort guarantees stable O(n log n) time by recursively dividing arrays and merging sorted halves. Heapsort uses a binary heap to sort in-place with guaranteed O(n log n) worst-case time."),
        ("tech-algo-binary-search", "Binary Search Algorithm", "algorithms",
         "Binary search is an efficient search algorithm for finding a target value within a sorted array. It compares the target with the middle element, eliminating half of the search space at each step. Binary search operates in O(log n) time complexity with O(1) auxiliary space."),
        ("tech-algo-recursion", "Recursion and Recursive Problem Solving", "algorithms",
         "Recursion is a method of solving computational problems where a function calls itself directly or indirectly to solve smaller instances of the same problem. Every valid recursive algorithm requires a base case to terminate execution without further recursion and a recursive step that progresses toward the base case."),
        ("tech-algo-dp", "Dynamic Programming (DP)", "algorithms",
         "Dynamic Programming (DP) is an algorithmic paradigm that solves complex optimization problems by breaking them into overlapping subproblems with optimal substructure. DP avoids redundant calculations by storing intermediate results using memoization (top-down) or tabulation (bottom-up), common in Knapsack and shortest-path problems."),
        ("tech-algo-greedy", "Greedy Algorithms", "algorithms",
         "A greedy algorithm makes the locally optimal choice at each stage with the intent of finding a global optimum. Greedy approaches are proven optimal for problems possessing the greedy-choice property and optimal substructure, such as Huffman coding, Kruskal's and Prim's minimum spanning tree algorithms, and Dijkstra's algorithm."),
        ("tech-algo-bfs-dfs", "Graph Traversal (Breadth-First Search and Depth-First Search)", "algorithms",
         "Breadth-First Search (BFS) explores a graph level by level using a queue, finding the shortest path in unweighted graphs in O(V + E) time. Depth-First Search (DFS) explores as deep as possible along each branch before backtracking using a stack or recursion, widely used in topological sorting and cycle detection."),
        ("tech-algo-dijkstra", "Dijkstra's Shortest Path Algorithm", "algorithms",
         "Dijkstra's algorithm finds the shortest path from a single source vertex to all other vertices in a weighted graph with non-negative edge weights. Using a min-priority queue (min-heap), it iteratively selects the unvisited vertex with the smallest provisional distance, achieving O((V + E) log V) time complexity.")
    ]
    for doc_id, title, topic, text in algo_data:
        docs.append({
            "document_id": doc_id,
            "passage_id": f"{doc_id}-1",
            "title": title,
            "domain": "computer_science",
            "topic": topic,
            "language": "en",
            "source_type": "curated",
            "keywords": [k.lower() for k in title.split()],
            "text": text
        })

    # 4. Object-Oriented Programming (OOP)
    oop_data = [
        ("tech-oop-principles", "Core Principles of Object-Oriented Programming (OOP)", "oop",
         "Object-Oriented Programming (OOP) is a programming paradigm based on the concept of 'objects' containing data (attributes) and code (methods). The four core pillars of OOP are Encapsulation (bundling data and restricting direct access), Abstraction (hiding implementation details), Inheritance (reusing characteristics from parent classes), and Polymorphism (allowing entities to take on multiple forms)."),
        ("tech-oop-solid", "SOLID Design Principles", "oop",
         "The SOLID principles are five design guidelines for maintainable object-oriented software: Single Responsibility (one reason to change), Open/Closed (open for extension, closed for modification), Liskov Substitution (subtypes must be substitutable for base types), Interface Segregation (small, client-specific interfaces), and Dependency Inversion (depend on abstractions, not concretions)."),
        ("tech-oop-patterns", "Software Design Patterns (Creational, Structural, Behavioral)", "oop",
         "Design patterns are reusable solutions to common software architecture problems. Creational patterns (Singleton, Factory, Builder) manage object instantiation. Structural patterns (Adapter, Composite, Decorator, Facade) compose classes and objects into larger structures. Behavioral patterns (Observer, Strategy, Command, State) define communication and responsibility between objects.")
    ]
    for doc_id, title, topic, text in oop_data:
        docs.append({
            "document_id": doc_id,
            "passage_id": f"{doc_id}-1",
            "title": title,
            "domain": "computer_science",
            "topic": topic,
            "language": "en",
            "source_type": "curated",
            "keywords": [k.lower() for k in title.split()],
            "text": text
        })

    # 5. Databases
    db_data = [
        ("tech-db-rdbms", "Relational Database Management Systems (RDBMS) and SQL", "databases",
         "A Relational Database Management System (RDBMS) organizes structured data into tables consisting of rows (records) and columns (attributes). Structured Query Language (SQL) is the standard declarative language used to query, insert, update, and manage relational databases like PostgreSQL, MySQL, and SQLite."),
        ("tech-db-acid", "ACID Transactions in Databases", "databases",
         "ACID is a set of four guarantees for reliable database transactions: Atomicity (all operations succeed or entire transaction rolls back), Consistency (transactions preserve valid database schema constraints), Isolation (concurrent transactions execute independently without interference), and Durability (committed changes persist permanently even after system crashes)."),
        ("tech-db-normalization", "Database Normalization (1NF, 2NF, 3NF, BCNF)", "databases",
         "Database normalization is the process of structuring relational tables to reduce data redundancy and improve data integrity. First Normal Form (1NF) eliminates repeating groups and enforces atomic values. Second Normal Form (2NF) removes partial dependencies on composite primary keys. Third Normal Form (3NF) removes transitive functional dependencies."),
        ("tech-db-indexing", "Database Indexing and B-Trees", "databases",
         "A database index is an auxiliary data structure that accelerates data retrieval queries at the cost of additional storage and write overhead. Most relational databases use self-balancing B-Trees or B+ Trees for primary and secondary indexes, allowing logarithmic O(log n) search, range scans, and sorting."),
        ("tech-db-nosql", "NoSQL Databases and Distributed Storage", "databases",
         "NoSQL databases provide non-relational, flexible data models optimized for horizontal scalability and high-throughput distributed applications. The four primary NoSQL categories are Document stores (MongoDB), Key-Value stores (Redis), Column-Family stores (Cassandra), and Graph databases (Neo4j).")
    ]
    for doc_id, title, topic, text in db_data:
        docs.append({
            "document_id": doc_id,
            "passage_id": f"{doc_id}-1",
            "title": title,
            "domain": "computer_science",
            "topic": topic,
            "language": "en",
            "source_type": "curated",
            "keywords": [k.lower() for k in title.split()],
            "text": text
        })

    # 6. Operating Systems
    os_data = [
        ("tech-os-processes-threads", "Processes, Threads, and Concurrency in Operating Systems", "operating_systems",
         "A process is an executing program instance with its own dedicated virtual memory space, file descriptors, and CPU context. A thread is the smallest unit of CPU execution within a process, sharing memory and resources with sibling threads. Concurrency is managed using synchronization primitives such as mutexes, semaphores, and condition variables."),
        ("tech-os-scheduling", "CPU Scheduling Algorithms in Operating Systems", "operating_systems",
         "CPU scheduling determines which ready process is allocated CPU execution time. Common scheduling algorithms include First-Come First-Served (FCFS), Shortest Job First (SJF), Round Robin (RR) with time quantum slices, and Multi-Level Feedback Queues (MLFQ) that balance responsiveness for interactive jobs with throughput for compute-bound tasks."),
        ("tech-os-virtual-memory", "Virtual Memory, Paging, and Page Faults", "operating_systems",
         "Virtual memory maps the program's virtual address space to physical RAM and secondary storage (swap space). Memory is divided into fixed-size pages mapped via page tables managed by the Memory Management Unit (MMU). When a requested page is not in physical memory, a page fault triggers the OS to fetch the page from disk using replacement algorithms such as LRU."),
        ("tech-os-deadlocks", "Deadlocks in Operating Systems", "operating_systems",
         "A deadlock occurs when a set of concurrent processes are permanently blocked because each process holds a resource while waiting for another resource held by another process. The four necessary Coffman conditions for deadlock are: Mutual Exclusion, Hold and Wait, No Preemption, and Circular Wait. Deadlocks are addressed via prevention, avoidance (Banker's Algorithm), or detection and recovery.")
    ]
    for doc_id, title, topic, text in os_data:
        docs.append({
            "document_id": doc_id,
            "passage_id": f"{doc_id}-1",
            "title": title,
            "domain": "computer_science",
            "topic": topic,
            "language": "en",
            "source_type": "curated",
            "keywords": [k.lower() for k in title.split()],
            "text": text
        })

    # 7. Networking & Web Development
    net_data = [
        ("tech-net-tcpip", "The TCP/IP Model and Internet Protocols", "networking",
         "The TCP/IP protocol suite powers the internet across four conceptual layers: Application (HTTP, DNS, SSH), Transport (TCP, UDP), Internet (IP, ICMP), and Link/Network Access (Ethernet, Wi-Fi). Transmission Control Protocol (TCP) provides reliable, ordered, error-checked data delivery via a three-way handshake and flow control, while UDP offers low-latency connectionless datagram delivery."),
        ("tech-net-http", "HTTP, HTTPS, and Web Protocols", "networking",
         "Hypertext Transfer Protocol (HTTP) is an application-layer request-response protocol for distributed hypermedia information systems. HTTPS encrypts HTTP communication using Transport Layer Security (TLS/SSL), protecting data integrity and confidentiality with asymmetric public-key cryptography and symmetric session encryption."),
        ("tech-net-rest", "REST Architecture and APIs", "web_development",
         "Representational State Transfer (REST) is an architectural style for networked web services. RESTful APIs use standard HTTP methods (GET, POST, PUT, DELETE, PATCH) to operate on stateless resource endpoints identified by Uniform Resource Identifiers (URIs), returning representations typically encoded in JSON format."),
        ("tech-net-websockets", "WebSockets and Real-Time Bidirectional Communication", "networking",
         "WebSocket is a computer communications protocol providing full-duplex, bidirectional communication channels over a single TCP connection. Initiated via an HTTP upgrade handshake, WebSockets enable low-overhead, real-time message exchange between client browsers and backend servers without HTTP polling overhead."),
        ("tech-web-react", "React Frontend Library and Virtual DOM", "web_development",
         "React is a declarative, component-based JavaScript library for building user interfaces developed by Meta. React uses a Virtual DOM to compute minimal UI diffs (reconciliation) before applying updates to the real browser DOM, featuring state hooks, effects, and functional components."),
        ("tech-web-fastapi", "FastAPI Modern Web Framework for Python", "web_development",
         "FastAPI is a modern, high-performance web framework for building APIs with Python 3.8+ based on standard Python type hints. Built upon Starlette for ASGI async routing and Pydantic for automated data validation and serialization, FastAPI generates interactive OpenAPI and Swagger documentation automatically with near-Go/NodeJS performance.")
    ]
    for doc_id, title, topic, text in net_data:
        docs.append({
            "document_id": doc_id,
            "passage_id": f"{doc_id}-1",
            "title": title,
            "domain": "computer_science",
            "topic": topic,
            "language": "en",
            "source_type": "curated",
            "keywords": [k.lower() for k in title.split()],
            "text": text
        })

    return docs
