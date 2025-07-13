// Simple heap implementation for YALPS
export class MinHeap {
    constructor(compareFn = (a, b) => a - b) {
        this.heap = [];
        this.compare = compareFn;
    }

    size() {
        return this.heap.length;
    }

    isEmpty() {
        return this.heap.length === 0;
    }

    empty() {
        return this.isEmpty();
    }

    peek() {
        return this.heap[0];
    }

    push(value) {
        this.heap.push(value);
        this.heapifyUp(this.heap.length - 1);
    }

    pop() {
        if (this.heap.length === 0) return undefined;
        
        const result = this.heap[0];
        const end = this.heap.pop();
        
        if (this.heap.length > 0) {
            this.heap[0] = end;
            this.heapifyDown(0);
        }
        
        return result;
    }

    heapifyUp(index) {
        while (index > 0) {
            const parentIndex = Math.floor((index - 1) / 2);
            if (this.compare(this.heap[index], this.heap[parentIndex]) >= 0) break;
            
            [this.heap[index], this.heap[parentIndex]] = [this.heap[parentIndex], this.heap[index]];
            index = parentIndex;
        }
    }

    heapifyDown(index) {
        while (true) {
            let minIndex = index;
            const leftChild = 2 * index + 1;
            const rightChild = 2 * index + 2;

            if (leftChild < this.heap.length && this.compare(this.heap[leftChild], this.heap[minIndex]) < 0) {
                minIndex = leftChild;
            }

            if (rightChild < this.heap.length && this.compare(this.heap[rightChild], this.heap[minIndex]) < 0) {
                minIndex = rightChild;
            }

            if (minIndex === index) break;

            [this.heap[index], this.heap[minIndex]] = [this.heap[minIndex], this.heap[index]];
            index = minIndex;
        }
    }
}

export default MinHeap;