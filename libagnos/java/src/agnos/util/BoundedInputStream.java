package agnos.util;

import java.io.EOFException;
import java.io.IOException;
import java.io.InputStream;

public class BoundedInputStream extends InputStream
{
	private InputStream inputStream;
	private int remainingLength;
	private boolean closeUnderlying;
	private boolean skipUnderlying;
	
	public BoundedInputStream(InputStream inputStream, int length, boolean skipUnderlying, boolean closeUnderlying) {
		this.inputStream = inputStream;
		this.remainingLength = length;
		this.skipUnderlying = skipUnderlying;
		this.closeUnderlying = closeUnderlying;
	}

	@Override
	public int available() throws IOException {
		return remainingLength;
	}
	
	@Override
	public void close() throws IOException {
		if (inputStream == null) {
			return;
		}
		if (skipUnderlying) {
			skip(-1);
		}
		if (closeUnderlying) {
			inputStream.close();
		}
		inputStream = ClosedInputStream.getInstance();
	}
	
	@Override
	public int read() throws IOException {
		byte[] buf = {0};
		if (read(buf, 0, buf.length) < 0) {
			return -1;
		}
		return buf[0];
	}

	@Override
	public int read(byte[] buf) throws IOException {
		return read(buf, 0, buf.length);
	}

	@Override
	public int read(byte[] buf, int off, int len) throws IOException {
		if (len > remainingLength) {
			throw new EOFException("request to read more than available");
		}
		int n = inputStream.read(buf, off, len);
		if (n > 0) {
			remainingLength -= n;
		}
		return n;
	}
	
	@Override
	public long skip(long n) throws IOException {
		if (n < 0 || n > remainingLength) {
			n = remainingLength;
		}
		if (n <= 0) {
			return 0;
		}
		n = inputStream.skip(n);
		remainingLength -= n;
		return n;
	}
}
