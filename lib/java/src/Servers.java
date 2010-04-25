package agnos;

import java.io.*;
import java.util.*;
import java.net.*;

public class Servers
{
	public abstract static class BaseServer
	{
		protected Protocol.BaseProcessor processor;
		protected ITransportFactory transportFactory;
		
		public BaseServer(Protocol.BaseProcessor processor, Transports.ITransportFactory transportFactory)
		{
			this.processor = processor;
			this.transportFactory = transportFactory;
		}
		
		public void serve() throws Exception
		{
			while (true)
			{
				ITransport transport = transportFactory.accept();
				_handleClient(transport);
				System.out.println("goodbye");
			}
		}

		protected abstract void _handleClient(ITransport transport) throws Exception;
	}

	public static class SimpleServer extends BaseServer
	{
		public SimpleServer(Protocol.BaseProcessor processor, Transports.ITransportFactory transportFactory)
		{
			super(processor, transportFactory);
		}

		protected void _handleClient(ITransport transport) throws Exception
		{
			InputStream inStream = transport.getInputStream();
			OutputStream outStream = transport.getOutputStream();
			
			try
			{
				while (true)
				{
					processor.process(inStream, outStream);
				}
			}
			catch (EOFException exc)
			{
				// finish on EOF
			}
			catch (SocketException exc)
			{
				System.out.println("!! SocketException: " + exc);
			}
		}
	}

	public static class ThreadedServer extends BaseServer
	{
		public ThreadedServer(Protocol.BaseProcessor processor, Transports.ITransportFactory transportFactory)
		{
			super(processor, transportFactory);
		}

		protected void _handleClient(ITransport transport) throws Exception
		{
			InputStream inStream = transport.getInputStream();
			OutputStream outStream = transport.getOutputStream();
		}
	}
	
	/*public abstract static class ChildServer
	{
		protected Process proc;
		public Protocol.BaseClient client;
		
		public ChildServer(ProcessBuilder procBuilder) throws IOException, UnknownHostException
		{
			Process p = procBuilder.start();
			InputStream stream = p.getInputStream();
			BufferedReader reader = new BufferedReader(new InputStreamReader(stream));
			String hostname = reader.readLine();
			String portstr = reader.readLine();
			stream.close();
			int port = Integer.parseInt(portstr);
			ITransport trans = new SocketTransport(hostname, port);
			client = getClient(trans);
		}
		
		protected abstract Protocol.BaseClient getClient(ITransport transport);
		
		public void close() throws IOException, InterruptedException
		{
			client.close();
			client = null;
			proc.waitFor();
		}
		
	}*/
}








